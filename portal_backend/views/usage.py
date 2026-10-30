import logging
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
                usage.PROBLEM_ACCOUNT_DOES_NOT_EXIST,
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
                403, usage.PROBLEM_ACCOUNT_DOES_NOT_EXIST, "Unknown account"
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
        public_key_pem = request.data.get("public_key_pem", "")
        label = request.data.get("label", "")
        if not isinstance(public_key_pem, str) or not isinstance(label, str):
            return Response(
                {"error": "public_key_pem and label must be strings"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            server_key = usage.register_key(organization, public_key_pem, label[:255])
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
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
