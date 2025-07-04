from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from ..services.relying_party import (
    create_relying_party,
    create_hostnames,
    create_condiscon,
    create_condiscon_attributes,
    make_condiscon_json,
    update_relying_party_hostnames,
    update_condiscon_context,
    update_condiscon_attributes,
    update_rp_environment,
    update_rp_slug,
)
from ..swagger_specs.relying_party import (
    relying_party_create_schema,
    relying_party_patch_schema,
    relying_party_delete_schema,
    relying_party_dns_status_schema,
    relying_party_list_schema,
)
from .permissions import IsOrganizationMaintainerOrAdmin
from ..models.model_serializers import (
    CondisconSerializer,
    RelyingPartyHostnameSerializer,
)
from ..models.models import (
    RelyingParty,
    RelyingPartyHostname,
    Organization,
    Condiscon,
    CondisconAttribute,
)
from django.core.exceptions import ValidationError


class RelyingPartyCreateView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsOrganizationMaintainerOrAdmin,
    ]

    @relying_party_create_schema
    @transaction.atomic
    def post(self, request: Request, org_slug: str) -> Response:

        try:
            relying_party = create_relying_party(
                request.data, org_slug, request.data.get("rp_slug")
            )
            hostnames = create_hostnames(
                request.data.get("hostnames", []), relying_party
            )
            if not hostnames:
                raise ValidationError("At least one hostname is required.")
            contexts = {}
            contexts["en"] = request.data.get("context_description_en", "")
            contexts["nl"] = request.data.get("context_description_nl", "")

            condiscon = create_condiscon(
                request.data.get("attributes", []), contexts, relying_party
            )
            create_condiscon_attributes(condiscon, request.data.get("attributes", []))
        except ValidationError as e:
            transaction.set_rollback(True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            transaction.set_rollback(True)
            return Response(
                {"error": "Failed to create relying party: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "slug": str(relying_party.rp_slug),
                "message": "Relying party registration successful",
                "hostnames": [
                    {"hostname": h.hostname, "dns_challenge": h.dns_challenge}
                    for h in hostnames
                ],
                "current_status": {
                    "ready": relying_party.ready,
                    "reviewed_accepted": relying_party.reviewed_accepted,
                    "published_at": relying_party.published_at,
                },
            },
            status=201,
        )


class RelyingPartyListView(APIView):
    permission_classes = [permissions.AllowAny]

    @relying_party_list_schema
    def get(self, request: Request, org_slug: str) -> Response:
        organization = get_object_or_404(Organization, slug=org_slug)
        relying_parties = RelyingParty.objects.filter(organization=organization)

        if not (
            request.user.is_authenticated
            and IsOrganizationMaintainerOrAdmin().has_permission(request, self)
        ):
            relying_parties = relying_parties.filter(published=True)

        return Response(
            {
                "relying_parties": [
                    {
                        "rp_slug": rp.rp_slug,
                        "environment": rp.yivi_tme.environment,
                        "status": rp.status,
                    }
                    for rp in relying_parties
                ]
            }
        )


class RelyingPartyRetrieveView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(
        self, request: Request, org_slug: str, environment: str, rp_slug: str
    ) -> Response:

        relying_party = get_object_or_404(
            RelyingParty,
            organization__slug=org_slug,
            yivi_tme__environment=environment,
            rp_slug=rp_slug,
        )

        if not (
            request.user.is_authenticated
            and IsOrganizationMaintainerOrAdmin().has_permission(request, self)
        ):
            if not relying_party.published:
                return Response(
                    {"error": "You are not allowed to view this relying party."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        hostnames = RelyingPartyHostname.objects.filter(relying_party=relying_party)
        condiscon = Condiscon.objects.filter(relying_party=relying_party).first()
        attributes, context_description_en, context_description_nl = [], "", ""

        if condiscon:
            condiscon_data = CondisconSerializer(condiscon).data
            condiscon_attributes = CondisconAttribute.objects.filter(
                condiscon=condiscon
            )
            attributes = [
                {
                    "credential_id": attr.credential_attribute.credential_id,
                    "credential_attribute_tag": attr.credential_attribute.name_en,
                    "reason_en": attr.reason_en,
                    "reason_nl": attr.reason_nl,
                }
                for attr in condiscon_attributes
            ]
            context_description_en = condiscon_data.get("context_description_en", "")
            context_description_nl = condiscon_data.get("context_description_nl", "")

        return Response(
            {
                "rp_slug": relying_party.rp_slug,
                "hostnames": RelyingPartyHostnameSerializer(hostnames, many=True).data,
                "context_description_en": context_description_en,
                "context_description_nl": context_description_nl,
                "attributes": attributes,
                "environment": relying_party.yivi_tme.environment,
                "published_at": relying_party.published_at,
                "ready": relying_party.ready,
                "status": relying_party.status,
            }
        )


class RelyingPartyDeleteView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsOrganizationMaintainerOrAdmin,
    ]

    @relying_party_delete_schema
    @transaction.atomic
    def delete(
        self, request: Request, org_slug: str, environment: str, rp_slug: str
    ) -> Response:
        rp = get_object_or_404(
            RelyingParty,
            organization__slug=org_slug,
            rp_slug=rp_slug,
            yivi_tme__environment=environment,
        )
        RelyingPartyHostname.objects.filter(
            relying_party=rp
        ).delete()  # TODO: we may wanna do this with signals in the future
        condiscons = Condiscon.objects.filter(relying_party=rp)
        for c in condiscons:
            CondisconAttribute.objects.filter(condiscon=c).delete()
        rp.delete()
        return Response(
            status=status.HTTP_200_OK,
            data={"message": "Relying party deleted successfully"},
        )


class RelyingPartyUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOrganizationMaintainerOrAdmin]

    @relying_party_patch_schema
    @transaction.atomic
    def patch(self, request: Request, org_slug: str, rp_slug: str) -> Response:
        try:
            relying_party = get_object_or_404(
                RelyingParty, organization__slug=org_slug, rp_slug=rp_slug
            )
            condiscon = Condiscon.objects.filter(relying_party=relying_party).first()

            data = request.data
            response_data = {"slug": str(relying_party.rp_slug)}
            updated_fields = set()

            def update_context():
                nonlocal condiscon
                if condiscon is None:
                    condiscon = create_condiscon(
                        attributes=data["attributes"],
                        contexts={
                            "en": data.get("context_description_en", ""),
                            "nl": data.get("context_description_nl", ""),
                        },
                        relying_party=relying_party,
                    )
                    create_condiscon_attributes(condiscon, data["attributes"])
                update_condiscon_context(condiscon, data)
                updated_fields.add("context")

            def update_attributes():
                nonlocal condiscon

                if condiscon is None:
                    condiscon = create_condiscon(
                        attributes=data["attributes"],
                        contexts={
                            "en": data.get("context_description_en", ""),
                            "nl": data.get("context_description_nl", ""),
                        },
                        relying_party=relying_party,
                    )
                    create_condiscon_attributes(condiscon, data["attributes"])
                else:
                    update_condiscon_attributes(condiscon, data["attributes"])
                    condiscon.condiscon = make_condiscon_json(data["attributes"])
                    condiscon.full_clean()
                    condiscon.save()

                updated_fields.add("attributes")

            def update_hostnames():
                dns_challenges = update_relying_party_hostnames(
                    relying_party, data["hostnames"]
                )
                if dns_challenges:
                    response_data["hostnames"] = dns_challenges
                updated_fields.add("hostnames")

            def update_environment():
                update_rp_environment(relying_party, data["environment"])
                updated_fields.add("environment")

            def update_slug():
                updated_slug = update_rp_slug(relying_party, data["rp_slug"])
                if updated_slug:
                    response_data["rp_slug"] = updated_slug
                updated_fields.add("rp_slug")

            dispatcher = {
                ("context_description_en", "context_description_nl"): update_context,
                ("attributes",): update_attributes,
                ("hostnames",): update_hostnames,
                ("environment",): update_environment,
                ("rp_slug",): update_slug,
            }

            for keys, handler in dispatcher.items():
                if any(k in data for k in keys):
                    handler()

            if "ready" in data:
                relying_party.ready = data["ready"]
                relying_party.ready_at = timezone.now() if relying_party.ready else None
                relying_party.reviewed_accepted = None
                relying_party.reviewed_at = None
                relying_party.rejection_remarks = None
                relying_party.published_at = (
                    None  # TODO: automatic public check not yet implemented
                )

            elif updated_fields:
                relying_party.ready = False
                relying_party.ready_at = None
                relying_party.reviewed_accepted = None
                relying_party.reviewed_at = None
                relying_party.rejection_remarks = None
                relying_party.published_at = None
            relying_party.full_clean()
            relying_party.save()

            response_data["message"] = "Relying party updated successfully"
            return Response(response_data, status=200)

        except ValidationError as e:
            transaction.set_rollback(True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            transaction.set_rollback(True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RelyingPartyHostnameStatusView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsOrganizationMaintainerOrAdmin,
    ]

    @relying_party_dns_status_schema
    def get(
        self, request: Request, org_slug: str, environment: str, rp_slug: str
    ) -> Response:
        """Get status of DNS verification for a hostname"""
        relying_party: RelyingParty = get_object_or_404(
            RelyingParty,
            organization__slug=org_slug,
            rp_slug=rp_slug,
            yivi_tme__environment=environment,
        )

        hostname: RelyingPartyHostname = get_object_or_404(
            RelyingPartyHostname, relying_party=relying_party
        )

        return Response(
            {RelyingPartyHostnameSerializer(hostname).data},
            status=status.HTTP_200_OK,
        )
