"""Usage reporting by self-hosted Yivi servers.

Servers report session counts over an ACME-shaped API (RFC 8555): every request is a flattened
JWS signed with the server's ES256 account key, carrying a single-use nonce and the request URL in
its protected header. The key is registered by an organization maintainer beforehand and is found
by its RFC 7638 JWK thumbprint.
"""

import base64
import calendar
import hashlib
import json
import secrets
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
from django.db import IntegrityError, transaction
from django.db.models import Q, Sum
from django.utils import timezone

from ..models.models import (
    USAGE_OUTCOME_CHOICES,
    UsageDisclosureCount,
    UsageNonce,
    UsageReport,
    UsageServerKey,
    UsageSessionCount,
)

NONCE_LIFETIME = timedelta(hours=1)
SUPPORTED_SCHEMAS = {1}
OUTCOMES = {value for value, _ in USAGE_OUTCOME_CHOICES}
ACTIONS = {"disclosing", "signing", "issuing"}

PROBLEM_MALFORMED = "urn:yivi:usage:error:malformed"
PROBLEM_BAD_NONCE = "urn:yivi:usage:error:badNonce"
PROBLEM_BAD_SIGNATURE = "urn:yivi:usage:error:badSignatureAlgorithm"
PROBLEM_UNAUTHORIZED = "urn:yivi:usage:error:unauthorized"
PROBLEM_KEY_NOT_REGISTERED = "urn:yivi:usage:error:keyNotRegistered"


class UsageProblem(Exception):
    """An error answered as an RFC 7807 problem document."""

    def __init__(self, status: int, type_: str, detail: str):
        super().__init__(detail)
        self.status = status
        self.type = type_
        self.detail = detail


def b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


# Keys


PEM_BEGIN = "-----BEGIN PUBLIC KEY-----"
PEM_END = "-----END PUBLIC KEY-----"
# A P-256 public key in PEM is under 200 characters; anything much longer is not one.
MAX_PEM_INPUT = 4096


def public_key_from_pem(pem: str) -> ec.EllipticCurvePublicKey:
    # Accept the whole output of `yivi irma server usage-key`, which also prints the
    # thumbprint. Plain string search, so the cost stays linear in the input.
    start = pem.find(PEM_BEGIN) if len(pem) <= MAX_PEM_INPUT else -1
    end = pem.find(PEM_END, start) if start >= 0 else -1
    if end < 0:
        raise ValueError("Not a PEM encoded public key")
    try:
        key = serialization.load_pem_public_key(
            pem[start : end + len(PEM_END)].encode()
        )
    except ValueError as e:
        raise ValueError("Not a PEM encoded public key") from e
    if not isinstance(key, ec.EllipticCurvePublicKey) or not isinstance(
        key.curve, ec.SECP256R1
    ):
        raise ValueError("The key must be an EC P-256 (ES256) public key")
    return key


def jwk_from_public_key(key: ec.EllipticCurvePublicKey) -> dict:
    numbers = key.public_numbers()
    return {
        "crv": "P-256",
        "kty": "EC",
        "x": b64encode(numbers.x.to_bytes(32, "big")),
        "y": b64encode(numbers.y.to_bytes(32, "big")),
    }


def public_key_from_jwk(jwk) -> ec.EllipticCurvePublicKey:
    # The jwk comes straight from a request's protected header, so it can be any JSON value.
    if not isinstance(jwk, dict):
        raise UsageProblem(400, PROBLEM_MALFORMED, "Invalid JWK")
    if jwk.get("kty") != "EC" or jwk.get("crv") != "P-256":
        raise UsageProblem(
            400, PROBLEM_BAD_SIGNATURE, "Only EC P-256 keys are supported"
        )
    try:
        x = int.from_bytes(b64decode(jwk["x"]), "big")
        y = int.from_bytes(b64decode(jwk["y"]), "big")
        return ec.EllipticCurvePublicNumbers(x, y, ec.SECP256R1()).public_key()
    except (KeyError, ValueError, TypeError) as e:
        raise UsageProblem(400, PROBLEM_MALFORMED, "Invalid JWK") from e


def thumbprint(key: ec.EllipticCurvePublicKey) -> str:
    """The RFC 7638 JWK thumbprint: SHA-256 over the required members in lexicographic order."""
    jwk = jwk_from_public_key(key)
    canonical = json.dumps(
        {name: jwk[name] for name in ("crv", "kty", "x", "y")}, separators=(",", ":")
    )
    return b64encode(hashlib.sha256(canonical.encode()).digest())


def pem_from_public_key(key: ec.EllipticCurvePublicKey) -> str:
    """The key's canonical PEM, without whatever else was pasted around it."""
    return key.public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()


def register_key(organization, public_key_pem: str, label: str = "") -> UsageServerKey:
    """Registers a server's public key for an organization. Raises ValueError for a bad key."""
    key = public_key_from_pem(public_key_pem)
    pem = pem_from_public_key(key)
    # A savepoint, so a duplicate key (IntegrityError) leaves the request's transaction usable.
    with transaction.atomic():
        return UsageServerKey.objects.create(
            organization=organization,
            public_key_pem=pem,
            thumbprint=thumbprint(key),
            label=label,
        )


# Nonces


def new_nonce() -> str:
    nonce = secrets.token_urlsafe(32)
    UsageNonce.objects.create(value=nonce)
    return nonce


def consume_nonce(value) -> None:
    if not isinstance(value, str):
        raise UsageProblem(400, PROBLEM_BAD_NONCE, "Missing nonce")
    deleted, _ = UsageNonce.objects.filter(
        value=value, created_at__gte=timezone.now() - NONCE_LIFETIME
    ).delete()
    if not deleted:
        raise UsageProblem(400, PROBLEM_BAD_NONCE, "Unknown or expired nonce")


def delete_expired_nonces() -> None:
    UsageNonce.objects.filter(created_at__lt=timezone.now() - NONCE_LIFETIME).delete()


# JWS


@dataclass
class VerifiedRequest:
    protected: dict
    payload: dict
    key: ec.EllipticCurvePublicKey


def parse_jws(body: bytes) -> tuple[dict, dict, str, bytes]:
    """Returns the protected header, the payload, the signing input and the signature."""
    try:
        jws = json.loads(body)
        protected = json.loads(b64decode(jws["protected"]))
        payload = json.loads(b64decode(jws["payload"])) if jws["payload"] else {}
        signature = b64decode(jws["signature"])
    except (ValueError, KeyError, TypeError) as e:
        raise UsageProblem(
            400, PROBLEM_MALFORMED, "Request is not a flattened JWS"
        ) from e
    if not isinstance(protected, dict) or not isinstance(payload, dict):
        raise UsageProblem(400, PROBLEM_MALFORMED, "Request is not a flattened JWS")
    signing_input = f"{jws['protected']}.{jws['payload']}"
    return protected, payload, signing_input, signature


def verify_signature(
    key: ec.EllipticCurvePublicKey, signing_input: str, signature: bytes
) -> None:
    if len(signature) != 64:
        raise UsageProblem(400, PROBLEM_MALFORMED, "Invalid ES256 signature")
    der = encode_dss_signature(
        int.from_bytes(signature[:32], "big"), int.from_bytes(signature[32:], "big")
    )
    try:
        key.verify(der, signing_input.encode(), ec.ECDSA(hashes.SHA256()))
    except InvalidSignature as e:
        raise UsageProblem(401, PROBLEM_UNAUTHORIZED, "Invalid signature") from e


def check_header(protected: dict, request_path: str) -> None:
    if protected.get("alg") != "ES256":
        raise UsageProblem(400, PROBLEM_BAD_SIGNATURE, "Only ES256 is supported")
    url = protected.get("url")
    # Only the path is compared: behind a reverse proxy the scheme and host the server used
    # may differ from what this process sees, and the path already pins the endpoint.
    if not isinstance(url, str) or not url.split("?")[0].endswith(request_path):
        raise UsageProblem(
            401, PROBLEM_UNAUTHORIZED, "The url in the JWS does not match"
        )


def verify_with_jwk(body: bytes, request_path: str) -> VerifiedRequest:
    """Verifies a JWS that carries its public key, as sent to look up an account."""
    protected, payload, signing_input, signature = parse_jws(body)
    check_header(protected, request_path)
    if "jwk" not in protected or "kid" in protected:
        raise UsageProblem(400, PROBLEM_MALFORMED, "Expected a jwk and no kid")
    key = public_key_from_jwk(protected["jwk"])
    verify_signature(key, signing_input, signature)
    consume_nonce(protected.get("nonce"))
    return VerifiedRequest(protected, payload, key)


def verify_with_kid(
    body: bytes, request_path: str, server_key: UsageServerKey, account_url: str
) -> VerifiedRequest:
    """Verifies a JWS signed by a registered account key, identified by its account URL."""
    protected, payload, signing_input, signature = parse_jws(body)
    check_header(protected, request_path)
    kid = protected.get("kid")
    if "jwk" in protected or not isinstance(kid, str):
        raise UsageProblem(400, PROBLEM_MALFORMED, "Expected a kid and no jwk")
    if kid.rstrip("/").split("/")[-1] != account_url.rstrip("/").split("/")[-1]:
        raise UsageProblem(
            401, PROBLEM_UNAUTHORIZED, "The kid does not match the account"
        )
    key = public_key_from_pem(server_key.public_key_pem)
    verify_signature(key, signing_input, signature)
    consume_nonce(protected.get("nonce"))
    if not server_key.is_active:
        raise UsageProblem(403, PROBLEM_UNAUTHORIZED, "The account key was deactivated")
    return VerifiedRequest(protected, payload, key)


# Reports


def _parse_time(value) -> datetime:
    if not isinstance(value, str):
        raise ValueError("expected a timestamp")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp without time zone")
    return parsed


# A heartbeat beyond a week says nothing useful about completeness; irmago caps it at 6 hours.
MAX_HEARTBEAT_SECONDS = 7 * 24 * 3600


def _heartbeat(value) -> int | None:
    """The optional heartbeat_seconds of a report. Servers before irmago 1.6 leave it out."""
    if value is None:
        return None
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
        or not 0 < value <= MAX_HEARTBEAT_SECONDS
    ):
        raise ValueError("invalid heartbeat_seconds")
    return value


def _row(row, with_credential_type: bool) -> dict:
    if not isinstance(row, dict):
        raise ValueError("expected an object")
    count = row.get("count")
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        raise ValueError("invalid count")
    if row.get("outcome") not in OUTCOMES:
        raise ValueError("invalid outcome")
    if row.get("action") not in ACTIONS:
        raise ValueError("invalid action")
    requestor = row.get("requestor", "")
    if not isinstance(requestor, str) or len(requestor) > 255:
        raise ValueError("invalid requestor")
    parsed = {
        "day": date.fromisoformat(row["day"]),
        "requestor": requestor,
        "action": row["action"],
        "outcome": row["outcome"],
        "count": count,
    }
    if with_credential_type:
        credential_type = row.get("credential_type")
        if not isinstance(credential_type, str) or not 0 < len(credential_type) <= 255:
            raise ValueError("invalid credential_type")
        parsed["credential_type"] = credential_type
    return parsed


def store_report(server_key: UsageServerKey, payload: dict) -> tuple[UsageReport, bool]:
    """Stores a report, or returns the one already stored under its report_id.

    Returns the report and whether it was newly created.
    """
    try:
        if payload.get("schema") not in SUPPORTED_SCHEMAS:
            raise ValueError("unsupported schema")
        report_id = payload["report_id"]
        if not isinstance(report_id, str) or not 0 < len(report_id) <= 64:
            raise ValueError("invalid report_id")
        sequence = payload["sequence"]
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence < 1:
            raise ValueError("invalid sequence")
        fields = {
            "schema": payload["schema"],
            "server_instance": str(payload["server_instance"])[:255],
            "run_id": str(payload["run_id"])[:64],
            "sequence": sequence,
            "final": payload.get("final") is True,
            "irmago_version": str(payload.get("irmago_version", ""))[:50],
            "period_from": _parse_time(payload["period"]["from"]),
            "period_to": _parse_time(payload["period"]["to"]),
            "heartbeat_seconds": _heartbeat(payload.get("heartbeat_seconds")),
        }
        disclosures = [_row(r, True) for r in payload.get("disclosures") or []]
        sessions = [_row(r, False) for r in payload.get("sessions") or []]
    except (KeyError, ValueError, TypeError) as e:
        raise UsageProblem(400, PROBLEM_MALFORMED, f"Invalid report: {e}") from e

    existing = UsageReport.objects.filter(
        server_key=server_key, report_id=report_id
    ).first()
    if existing:
        return existing, False
    try:
        with transaction.atomic():
            report = UsageReport.objects.create(
                server_key=server_key, report_id=report_id, **fields
            )
            UsageDisclosureCount.objects.bulk_create(
                UsageDisclosureCount(report=report, **row) for row in disclosures
            )
            UsageSessionCount.objects.bulk_create(
                UsageSessionCount(report=report, **row) for row in sessions
            )
    except IntegrityError:
        # The same report arrived twice at the same time; the other request stored it.
        return UsageReport.objects.get(
            server_key=server_key, report_id=report_id
        ), False
    return report, True


# A run's missing sequence numbers are listed up to this many; missing_count has the total.
MAX_LISTED_MISSING = 100


def _missing_sequences(sequences: list[int]) -> tuple[list[int], int]:
    """The first MAX_LISTED_MISSING missing numbers in 1..max(sequences), and how many are missing.

    A server picks its own sequence numbers, so the cost follows the number of reports,
    never the size of the highest number.
    """
    listed: list[int] = []
    count = 0
    previous = 0
    for sequence in sorted(set(sequences)):
        gap_start, gap_end = previous + 1, sequence
        count += gap_end - gap_start
        room = MAX_LISTED_MISSING - len(listed)
        if room > 0:
            listed.extend(range(gap_start, min(gap_end, gap_start + room)))
        previous = sequence
    return listed, count


def find_gaps(reports) -> list[dict]:
    """Lists runs whose reports may be incomplete: a missing sequence number, or no final report.

    The run a server is currently in has no final report yet either; it is listed with
    final=False, and readers judge it by its last report time.
    """
    runs: dict[tuple, list] = {}
    for report in reports:
        runs.setdefault((report.server_key_id, report.run_id), []).append(report)
    gaps = []
    for (_, run_id), run in runs.items():
        missing, missing_count = _missing_sequences([r.sequence for r in run])
        final = any(r.final for r in run)
        if missing_count or not final:
            last = max(run, key=lambda r: r.sequence)
            gaps.append(
                {
                    "server_instance": last.server_instance,
                    "run_id": run_id,
                    "missing_sequences": missing,
                    "missing_count": missing_count,
                    "final": final,
                    "last_report_at": last.period_to,
                }
            )
    return gaps


# Overviews


def daily_verifications(reports, year: int, month: int) -> list[dict]:
    """Successful verifications (completed disclosure sessions) per day of a month.

    Every day of the month gets an entry, so days without verifications show as 0.
    """
    first = date(year, month, 1)
    last = date(year, month, calendar.monthrange(year, month)[1])
    totals = dict(
        UsageSessionCount.objects.filter(
            report__in=reports,
            action="disclosing",
            outcome="done",
            day__range=(first, last),
        )
        .values_list("day")
        .annotate(total=Sum("count"))
    )
    return [
        {
            "day": first + timedelta(days=i),
            "count": totals.get(first + timedelta(days=i), 0),
        }
        for i in range((last - first).days + 1)
    ]


def run_overview(reports, limit: int = 20) -> list[dict]:
    """The most recently reporting runs, newest first, with how complete each one is."""
    runs: dict[tuple, list] = {}
    for report in reports.only(
        "server_key_id", "run_id", "sequence", "final", "server_instance", "period_to"
    ):
        runs.setdefault((report.server_key_id, report.run_id), []).append(report)
    overview = []
    for (_, run_id), run in runs.items():
        last = max(run, key=lambda r: r.sequence)
        _, missing_count = _missing_sequences([r.sequence for r in run])
        overview.append(
            {
                "run_id": run_id,
                "server_instance": last.server_instance,
                "reports": len(run),
                "last_sequence": last.sequence,
                "missing_count": missing_count,
                "final": any(r.final for r in run),
                "last_report_at": max(r.period_to for r in run),
            }
        )
    overview.sort(key=lambda r: r["last_report_at"], reverse=True)
    return overview[:limit]


# Monthly usage, for invoicing

# What Trusted Verifiers are billed for: completed disclosure and signature sessions.
BILLED_ACTIONS = ("disclosing", "signing")
BILLED_OUTCOMES = ("done",)

# How long a server may stay silent beyond its heartbeat before that counts as a gap: a report is
# sealed up to a tick late, and a failed send is retried with backoff.
HEARTBEAT_GRACE = timedelta(minutes=15)

# Kinds of gaps in a month's reports. Each makes the month's numbers possibly incomplete.
GAP_NO_KEY = "no_key"  # no usage key was active, and no report covers the period
GAP_NO_REPORTS = "no_reports"  # a key was active, but no server reported at all
GAP_MISSING_REPORTS = "missing_reports"  # a run's sequence numbers skip reports
GAP_INTERRUPTED = "interrupted"  # a run stopped reporting without a final report
# The server skips quiet intervals, so a period without its reports may be quiet or an outage.
GAP_NO_HEARTBEAT = "no_heartbeat"

Interval = tuple[datetime, datetime]


def month_days(year: int, month: int) -> tuple[date, date]:
    return date(year, month, 1), date(year, month, calendar.monthrange(year, month)[1])


def monthly_usage(
    organization,
    year: int,
    month: int,
    actions=BILLED_ACTIONS,
    outcomes=BILLED_OUTCOMES,
) -> dict:
    """Usage of one month per requestor and credential type, with the gaps in its reports.

    `sessions` counts every session once. `credentials` counts, per credential type, the
    sessions that disclosed it (outcome done) or asked for it (other outcomes), so a session
    that disclosed three credential types is in three of its rows: sum `sessions` to count
    sessions, never `credentials`.
    """
    first, last = month_days(year, month)
    reports = UsageReport.objects.filter(server_key__organization=organization)
    filters = {
        "report__in": reports,
        "day__range": (first, last),
        "action__in": list(actions),
        "outcome__in": list(outcomes),
    }
    sessions = (
        UsageSessionCount.objects.filter(**filters)
        .values("requestor", "action", "outcome")
        .annotate(count=Sum("count"))
        .order_by("requestor", "action", "outcome")
    )
    credentials = (
        UsageDisclosureCount.objects.filter(**filters)
        .values("requestor", "action", "outcome", "credential_type")
        .annotate(count=Sum("count"))
        .order_by("requestor", "action", "outcome", "credential_type")
    )
    return {
        "month": f"{year:04d}-{month:02d}",
        "actions": list(actions),
        "outcomes": list(outcomes),
        "sessions": list(sessions),
        "credentials": list(credentials),
        "completeness": month_completeness(organization, year, month),
    }


def _merge(intervals: list[Interval]) -> list[Interval]:
    merged: list[Interval] = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def _subtract(intervals: list[Interval], covered: list[Interval]) -> list[Interval]:
    """The parts of the intervals that the covered intervals leave open."""
    result = []
    for start, end in intervals:
        pieces = [(start, end)]
        for c_start, c_end in covered:
            remaining = []
            for p_start, p_end in pieces:
                if c_end <= p_start or c_start >= p_end:
                    remaining.append((p_start, p_end))
                    continue
                if p_start < c_start:
                    remaining.append((p_start, c_start))
                if c_end < p_end:
                    remaining.append((c_end, p_end))
            pieces = remaining
        result.extend(pieces)
    return result


RUN_FIELDS = (
    "server_key_id",
    "run_id",
    "sequence",
    "final",
    "server_instance",
    "irmago_version",
    "heartbeat_seconds",
    "period_from",
    "period_to",
)


def _runs_around(reports, start: datetime, end: datetime) -> dict[tuple, list]:
    """The runs with a report in [start, end], and per server instance the last run before
    start, so a run that went silent before the month is judged too. Reports are sorted by
    sequence."""
    run_keys = set(
        reports.filter(period_to__gte=start, period_from__lte=end)
        .values_list("server_key_id", "run_id")
        .distinct()
    )
    instances = (
        reports.filter(period_to__lt=start)
        .values_list("server_key_id", "server_instance")
        .distinct()
    )
    for server_key_id, server_instance in instances:
        before = (
            reports.filter(
                server_key_id=server_key_id,
                server_instance=server_instance,
                period_to__lt=start,
            )
            .order_by("-period_to")
            .values_list("server_key_id", "run_id")
            .first()
        )
        if before:
            run_keys.add(before)
    if not run_keys:
        return {}
    query = Q()
    for server_key_id, run_id in run_keys:
        query |= Q(server_key_id=server_key_id, run_id=run_id)
    runs: dict[tuple, list] = {}
    for report in reports.filter(query).only(*RUN_FIELDS):
        runs.setdefault((report.server_key_id, report.run_id), []).append(report)
    for run in runs.values():
        run.sort(key=lambda r: r.sequence)
    return runs


def month_completeness(organization, year: int, month: int, now=None) -> dict:
    """Lists the periods of a month whose usage may not have been reported.

    A period counts as reported when a report covers it, or when the server had ended its run
    cleanly (a stopped server has no sessions). Gaps are clipped to the month, and to now for
    the current month. A server without a heartbeat skips quiet intervals, so a period without
    its reports cannot be judged; such a server is listed once, as no_heartbeat.
    """
    now = now or timezone.now()
    first, last = month_days(year, month)
    start = datetime.combine(first, time.min, tzinfo=UTC)
    end = min(datetime.combine(last + timedelta(days=1), time.min, tzinfo=UTC), now)
    if end <= start:
        return {"complete": True, "reported_until": None, "gaps": []}

    reports = UsageReport.objects.filter(server_key__organization=organization)
    runs = _runs_around(reports, start, end)
    covered = _merge(
        [(r.period_from, r.period_to) for run in runs.values() for r in run]
    )
    gaps: list[dict] = []

    def add(kind, gap_from, gap_to, server_instance="", **extra):
        gap_from, gap_to = max(gap_from, start), min(gap_to, end)
        if gap_from < gap_to:
            gaps.append(
                {
                    "kind": kind,
                    "from": gap_from,
                    "to": gap_to,
                    "server_instance": server_instance,
                    **extra,
                }
            )

    # Periods without an active key, unless reports cover them anyway: a server keeps its
    # counts until its key is registered, and sends them afterwards.
    active = _merge(
        [
            (key.created_at, key.deactivated_at or end)
            for key in organization.usage_keys.all()
            if key.created_at < (key.deactivated_at or end)
        ]
    )
    for gap_from, gap_to in _subtract(_subtract([(start, end)], active), covered):
        add(GAP_NO_KEY, gap_from, gap_to)

    if not runs:
        for gap_from, gap_to in active:
            add(GAP_NO_REPORTS, gap_from, gap_to)

    by_instance: dict[tuple, list] = {}
    for (server_key_id, _), run in runs.items():
        by_instance.setdefault((server_key_id, run[-1].server_instance), []).append(run)
    for (_, instance), instance_runs in by_instance.items():
        instance_runs.sort(key=lambda run: run[0].period_from)
        for i, run in enumerate(instance_runs):
            if run[0].sequence > 1:
                # The first reports of the run never arrived; when they started is unknown.
                add(
                    GAP_MISSING_REPORTS,
                    instance_runs[i - 1][-1].period_to if i else start,
                    run[0].period_from,
                    instance,
                    missing_count=run[0].sequence - 1,
                )
            for previous, report in zip(run, run[1:], strict=False):
                if report.sequence > previous.sequence + 1:
                    add(
                        GAP_MISSING_REPORTS,
                        previous.period_to,
                        report.period_from,
                        instance,
                        missing_count=report.sequence - previous.sequence - 1,
                    )
            last_report = run[-1]
            if last_report.final:
                continue
            if i + 1 < len(instance_runs):
                # A later run started without this one ending cleanly: the server stopped
                # unexpectedly, and what it counted after its last report is lost.
                add(
                    GAP_INTERRUPTED,
                    last_report.period_to,
                    instance_runs[i + 1][0].period_from,
                    instance,
                )
            elif last_report.heartbeat_seconds is not None:
                heartbeat = timedelta(seconds=last_report.heartbeat_seconds)
                if last_report.period_to + heartbeat + HEARTBEAT_GRACE < end:
                    add(GAP_INTERRUPTED, last_report.period_to, end, instance)

        old_runs = [run for run in instance_runs if run[-1].heartbeat_seconds is None]
        if old_runs:
            last_old = old_runs[-1]
            running = last_old is instance_runs[-1] and not last_old[-1].final
            add(
                GAP_NO_HEARTBEAT,
                old_runs[0][0].period_from,
                end if running else last_old[-1].period_to,
                instance,
                irmago_version=last_old[-1].irmago_version,
            )

    gaps.sort(key=lambda gap: (gap["from"], gap["kind"], gap["server_instance"]))
    return {
        "complete": not gaps,
        "reported_until": max(
            (r.period_to for run in runs.values() for r in run), default=None
        ),
        "gaps": gaps,
    }
