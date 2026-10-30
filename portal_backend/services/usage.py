"""Usage reporting by self-hosted Yivi servers.

Servers report session counts over an ACME-shaped API (RFC 8555): every request is a flattened
JWS signed with the server's ES256 account key, carrying a single-use nonce and the request URL in
its protected header. The key is registered by an organization maintainer beforehand and is found
by its RFC 7638 JWK thumbprint.
"""

import base64
import hashlib
import json
import re
import secrets
from dataclasses import dataclass
from datetime import date, datetime, timedelta

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature
from django.db import IntegrityError, transaction
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

PROBLEM_MALFORMED = "urn:ietf:params:acme:error:malformed"
PROBLEM_BAD_NONCE = "urn:ietf:params:acme:error:badNonce"
PROBLEM_BAD_SIGNATURE = "urn:ietf:params:acme:error:badSignatureAlgorithm"
PROBLEM_UNAUTHORIZED = "urn:ietf:params:acme:error:unauthorized"
PROBLEM_ACCOUNT_DOES_NOT_EXIST = "urn:ietf:params:acme:error:accountDoesNotExist"


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


PEM_PUBLIC_KEY = re.compile(
    r"-----BEGIN PUBLIC KEY-----.+?-----END PUBLIC KEY-----", re.DOTALL
)


def public_key_from_pem(pem: str) -> ec.EllipticCurvePublicKey:
    # Accept the whole output of `irma server usage-key`, which also prints the thumbprint.
    match = PEM_PUBLIC_KEY.search(pem)
    if match is None:
        raise ValueError("Not a PEM encoded public key")
    try:
        key = serialization.load_pem_public_key(match.group(0).encode())
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


def public_key_from_jwk(jwk: dict) -> ec.EllipticCurvePublicKey:
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


def register_key(organization, public_key_pem: str, label: str = "") -> UsageServerKey:
    """Registers a server's public key for an organization. Raises ValueError for a bad key."""
    key = public_key_from_pem(public_key_pem)
    pem = key.public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
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
        sequences = sorted(r.sequence for r in run)
        missing = sorted(set(range(1, sequences[-1] + 1)) - set(sequences))
        final = any(r.final for r in run)
        if missing or not final:
            last = max(run, key=lambda r: r.sequence)
            gaps.append(
                {
                    "server_instance": last.server_instance,
                    "run_id": run_id,
                    "missing_sequences": missing,
                    "final": final,
                    "last_report_at": last.period_to,
                }
            )
    return gaps
