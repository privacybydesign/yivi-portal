import csv
import logging
import re
from datetime import date
from typing import ClassVar

from django.db import IntegrityError
from django.db.models import Sum
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models.models import (
    USAGE_OUTCOME_CHOICES,
    Organization,
    UsageDisclosureCount,
    UsageReport,
    UsageServerKey,
    UsageSessionCount,
)
from ..services import usage
from .permissions import IsOrganizationMaintainerOrAdmin

logger = logging.getLogger(__name__)


# The ACME-shaped API the Yivi server talks to. It authenticates by JWS, not by session or
# token, so these are plain Django views without CSRF protection.


def _with_nonce(response: HttpResponse) -> HttpResponse:
    response["Replay-Nonce"] = usage.new_nonce()
    response["Cache-Control"] = "no-store"
    return response


def _problem(problem: usage.UsageProblem) -> HttpResponse:
    response = JsonResponse(
        {"type": problem.type, "detail": problem.detail}, status=problem.status
    )
    response["Content-Type"] = "application/problem+json"
    return _with_nonce(response)


def _account_url(request: HttpRequest, server_key: UsageServerKey) -> str:
    return request.build_absolute_uri(
        reverse("portal_backend:usage-account", args=[server_key.id])
    )


@require_http_methods(["GET"])
def usage_directory(request: HttpRequest) -> HttpResponse:
    return JsonResponse(
        {
            "newNonce": request.build_absolute_uri(
                reverse("portal_backend:usage-new-nonce")
            ),
            "newAccount": request.build_absolute_uri(
                reverse("portal_backend:usage-new-account")
            ),
        }
    )


@require_http_methods(["HEAD", "GET"])
def usage_new_nonce(request: HttpRequest) -> HttpResponse:
    usage.delete_expired_nonces()
    status_code = 200 if request.method == "HEAD" else 204
    return _with_nonce(HttpResponse(status=status_code))


@csrf_exempt
@require_http_methods(["POST"])
def usage_new_account(request: HttpRequest) -> HttpResponse:
    """Looks up the account of a registered key. Keys are registered by organization
    maintainers in the Portal, never by the server itself, so only onlyReturnExisting is
    supported."""
    try:
        verified = usage.verify_with_jwk(request.body, request.path)
        if verified.payload.get("onlyReturnExisting") is not True:
            raise usage.UsageProblem(
                403,
                usage.PROBLEM_UNAUTHORIZED,
                "Register the key with your organization in the Yivi Portal",
            )
        server_key = UsageServerKey.objects.filter(
            thumbprint=usage.thumbprint(verified.key), deactivated_at__isnull=True
        ).first()
        if server_key is None:
            raise usage.UsageProblem(
                400,
                usage.PROBLEM_KEY_NOT_REGISTERED,
                "This key is not registered in the Yivi Portal, or was deactivated",
            )
    except usage.UsageProblem as problem:
        return _problem(problem)

    response = JsonResponse(
        {"status": "valid", "organization": server_key.organization.slug}
    )
    response["Location"] = _account_url(request, server_key)
    return _with_nonce(response)


@csrf_exempt
@require_http_methods(["POST"])
def usage_account(request: HttpRequest, key_id) -> HttpResponse:
    # The account URL is the kid; posting to it is not supported.
    return _problem(
        usage.UsageProblem(405, usage.PROBLEM_MALFORMED, "Use the reports endpoint")
    )


@csrf_exempt
@require_http_methods(["POST"])
def usage_reports(request: HttpRequest, key_id) -> HttpResponse:
    try:
        server_key = UsageServerKey.objects.filter(id=key_id).first()
        if server_key is None:
            raise usage.UsageProblem(
                403, usage.PROBLEM_KEY_NOT_REGISTERED, "Unknown account"
            )
        verified = usage.verify_with_kid(
            request.body, request.path, server_key, _account_url(request, server_key)
        )
        report, created = usage.store_report(server_key, verified.payload)
    except usage.UsageProblem as problem:
        return _problem(problem)

    if created:
        logger.info(
            "Stored usage report %s #%s from %s for %s",
            report.run_id,
            report.sequence,
            report.server_instance,
            server_key.organization.slug,
        )
    return _with_nonce(
        JsonResponse(
            {"report_id": report.report_id, "received_at": report.received_at},
            status=201 if created else 200,
        )
    )


# The maintainer API: registering server keys and reading usage.


class UsageServerKeySerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = UsageServerKey
        fields: ClassVar[list] = [
            "id",
            "label",
            "public_key_pem",
            "thumbprint",
            "created_at",
            "deactivated_at",
            "is_active",
        ]
        read_only_fields: ClassVar[list] = [
            "id",
            "thumbprint",
            "created_at",
            "deactivated_at",
            "is_active",
        ]


class UsageServerKeysView(APIView):
    permission_classes: ClassVar[list] = [IsOrganizationMaintainerOrAdmin]

    def get(self, request: Request, org_slug: str) -> Response:
        """Lists the usage reporting keys of an organization."""
        organization = get_object_or_404(Organization, slug=org_slug)
        keys = organization.usage_keys.order_by("-created_at")
        return Response(UsageServerKeySerializer(keys, many=True).data)

    def post(self, request: Request, org_slug: str) -> Response:
        """Registers the public key a Yivi server prints with `irma server usage-key`."""
        organization = get_object_or_404(Organization, slug=org_slug)
        if not organization.is_verified:
            # Usage is only collected for organizations Yivi has verified.
            return Response(
                {"error": "The organization must be verified to register usage keys"},
                status=status.HTTP_403_FORBIDDEN,
            )
        public_key_pem = request.data.get("public_key_pem", "")
        label = request.data.get("label", "")
        if not isinstance(public_key_pem, str) or not isinstance(label, str):
            return Response(
                {"error": "public_key_pem and label must be strings"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            server_key = usage.register_key(organization, public_key_pem, label[:255])
        except ValueError:
            logger.exception("Invalid usage server key registration input")
            return Response(
                {"error": "Invalid key registration request"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except IntegrityError:
            return Response(
                {"error": "This key is already registered"},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(
            UsageServerKeySerializer(server_key).data, status=status.HTTP_201_CREATED
        )


class UsageServerKeyView(APIView):
    permission_classes: ClassVar[list] = [IsOrganizationMaintainerOrAdmin]

    def delete(self, request: Request, org_slug: str, key_id) -> Response:
        """Deactivates a key, e.g. when it was lost or compromised. Reports it already sent
        are kept."""
        server_key = get_object_or_404(
            UsageServerKey, id=key_id, organization__slug=org_slug
        )
        if server_key.deactivated_at is None:
            server_key.deactivated_at = timezone.now()
            server_key.save(update_fields=["deactivated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class UsageSummaryView(APIView):
    permission_classes: ClassVar[list] = [IsOrganizationMaintainerOrAdmin]

    def get(self, request: Request, org_slug: str) -> Response:
        """Usage per day, requestor, credential type and outcome, summed over all reports of
        the organization's servers. Optional `from` and `to` (YYYY-MM-DD) bound the days."""
        organization = get_object_or_404(Organization, slug=org_slug)
        try:
            day_from = (
                date.fromisoformat(request.query_params["from"])
                if "from" in request.query_params
                else None
            )
            day_to = (
                date.fromisoformat(request.query_params["to"])
                if "to" in request.query_params
                else None
            )
        except ValueError:
            return Response(
                {"error": "from and to must be dates (YYYY-MM-DD)"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        reports = UsageReport.objects.filter(server_key__organization=organization)
        disclosures = UsageDisclosureCount.objects.filter(report__in=reports)
        sessions = UsageSessionCount.objects.filter(report__in=reports)
        if day_from:
            disclosures, sessions = (
                disclosures.filter(day__gte=day_from),
                sessions.filter(day__gte=day_from),
            )
        if day_to:
            disclosures, sessions = (
                disclosures.filter(day__lte=day_to),
                sessions.filter(day__lte=day_to),
            )

        return Response(
            {
                "disclosures": list(
                    disclosures.values(
                        "day", "requestor", "action", "credential_type", "outcome"
                    )
                    .annotate(count=Sum("count"))
                    .order_by(
                        "day", "requestor", "action", "credential_type", "outcome"
                    )
                ),
                "sessions": list(
                    sessions.values("day", "requestor", "action", "outcome")
                    .annotate(count=Sum("count"))
                    .order_by("day", "requestor", "action", "outcome")
                ),
                "gaps": usage.find_gaps(
                    reports.only(
                        "server_key_id",
                        "run_id",
                        "sequence",
                        "final",
                        "server_instance",
                        "period_to",
                    )
                ),
            }
        )


MONTH_PATTERN = re.compile(r"[0-9]{4}-[0-9]{2}")
MONTH_QUERY_ERROR = {
    "error": "month must be YYYY-MM; action must be disclosing, signing or issuing; "
    "outcome must be done, cancelled, failed or timeout"
}


def _month_query(request: Request) -> tuple[int, int, list[str], list[str]]:
    """The month (YYYY-MM) and the actions and outcomes to count, from the query string.

    Without actions or outcomes, counts what is billed: completed disclosures and signatures.
    Raises ValueError for anything else.
    """
    value = request.query_params.get("month", "")
    if not MONTH_PATTERN.fullmatch(value):
        raise ValueError("month must be YYYY-MM")
    year, month = int(value[:4]), int(value[5:])
    # Usage reporting began in 2026; the upper bound keeps the end of the month a valid date.
    if not 1 <= month <= 12 or not 2000 <= year <= 9998:
        raise ValueError("month must be YYYY-MM")
    actions = request.query_params.getlist("action") or list(usage.BILLED_ACTIONS)
    outcomes = request.query_params.getlist("outcome") or list(usage.BILLED_OUTCOMES)
    if not set(actions) <= usage.ACTIONS or not set(outcomes) <= usage.OUTCOMES:
        raise ValueError("unknown action or outcome")
    # A fixed order, so the same selection always gives the same answer and file.
    actions = sorted(set(actions))
    outcomes = [o for o, _ in USAGE_OUTCOME_CHOICES if o in outcomes]
    return year, month, actions, outcomes


class UsageMonthlyView(APIView):
    permission_classes: ClassVar[list] = [IsOrganizationMaintainerOrAdmin]

    def get(self, request: Request, org_slug: str) -> Response:
        """Usage of one month per requestor and credential type, for invoicing, with the gaps
        in the reports. Query: `month` (YYYY-MM), and optionally `action` and `outcome`, each
        repeatable; they default to completed (`done`) `disclosing` and `signing` sessions."""
        organization = get_object_or_404(Organization, slug=org_slug)
        try:
            year, month, actions, outcomes = _month_query(request)
        except ValueError:
            return Response(MONTH_QUERY_ERROR, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            usage.monthly_usage(organization, year, month, actions, outcomes)
        )


# Spreadsheet programs run a cell that starts with one of these as a formula. Requestor names
# and credential types come from the organization's servers, so they are neutralised.
CSV_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _csv_cell(value) -> str:
    text = "" if value is None else str(value)
    return "'" + text if text.startswith(CSV_FORMULA_PREFIXES) else text


class UsageMonthlyCsvView(APIView):
    permission_classes: ClassVar[list] = [IsOrganizationMaintainerOrAdmin]

    def get(self, request: Request, org_slug: str) -> HttpResponse:
        """The monthly usage as CSV, one row per count. A `sessions` row counts sessions; a
        `credentials` row counts the sessions that disclosed one credential type. `complete` is
        false when the month's reports have gaps; the gaps follow as `gap` rows."""
        organization = get_object_or_404(Organization, slug=org_slug)
        try:
            year, month, actions, outcomes = _month_query(request)
        except ValueError:
            return Response(MONTH_QUERY_ERROR, status=status.HTTP_400_BAD_REQUEST)
        data = usage.monthly_usage(organization, year, month, actions, outcomes)
        complete = "true" if data["completeness"]["complete"] else "false"

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response["Content-Disposition"] = (
            f'attachment; filename="yivi-usage-{organization.slug}-{data["month"]}.csv"'
        )
        writer = csv.writer(response)
        writer.writerow(
            [
                "month",
                "organization",
                "complete",
                "metric",
                "requestor",
                "action",
                "outcome",
                "credential_type",
                "count",
                "gap_from",
                "gap_to",
                "server_instance",
            ]
        )
        common = [data["month"], organization.slug, complete]
        for row in data["sessions"]:
            writer.writerow(
                [
                    *common,
                    "sessions",
                    _csv_cell(row["requestor"]),
                    row["action"],
                    row["outcome"],
                    "",
                    row["count"],
                    "",
                    "",
                    "",
                ]
            )
        for row in data["credentials"]:
            writer.writerow(
                [
                    *common,
                    "credentials",
                    _csv_cell(row["requestor"]),
                    row["action"],
                    row["outcome"],
                    _csv_cell(row["credential_type"]),
                    row["count"],
                    "",
                    "",
                    "",
                ]
            )
        for gap in data["completeness"]["gaps"]:
            writer.writerow(
                [
                    *common,
                    f"gap:{gap['kind']}",
                    "",
                    "",
                    "",
                    "",
                    "",
                    gap["from"].isoformat(),
                    gap["to"].isoformat(),
                    _csv_cell(gap["server_instance"]),
                ]
            )
        return response
