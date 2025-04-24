from typing import Any, Dict, List, Optional, Union

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg import openapi  # type: ignore
from drf_yasg.utils import swagger_auto_schema  # type: ignore
from rest_framework import permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .helpers import IsMaintainerOrAdmin, BelongsToOrganization
from ..dns_verification import generate_dns_challenge
from ..models.model_serializers import (
    CondisconSerializer,
    RelyingPartyHostnameSerializer,
)
from ..models.models import (
    RelyingParty,
    RelyingPartyHostname,
    YiviTrustModelEnv,
    Organization,
    Condiscon,
    CondisconAttribute,
    CredentialAttribute,
)


def check_existing_hostname(request: Request) -> Optional[Response]:
    hostname_data = request.data.get("hostnames")

    if not isinstance(hostname_data, list):
        hostname_data = [hostname_data]

        #  TODO: better check for existing hostnames


class RelyingPartyListCreateView(APIView):

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [
            IsAuthenticated(),
            BelongsToOrganization(),
            IsMaintainerOrAdmin(),
        ]

    def make_condiscon_from_attributes(
        self, attributes_data: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        condiscon_json = {
            "@context": "https://irma.app/ld/request/disclosure/v2",
            "disclose": [[]],
        }

        credential_attributes: Dict[int, List[str]] = {}

        for attr in attributes_data:
            credential_attribute = get_object_or_404(
                CredentialAttribute,
                name=attr["credential_attribute_name"],
            )
            credential_id = credential_attribute.credential.id

            if credential_id not in credential_attributes:
                credential_attributes[credential_id] = []

            credential_attributes[credential_id].append(credential_attribute.name)

        for credential_id, attribute_list in credential_attributes.items():
            condiscon_json["disclose"][0].append(attribute_list)

        return condiscon_json

    def save_rp(self, request: Any, org_slug: str, rp_slug: str) -> RelyingParty:
        yivi_tme = get_object_or_404(
            YiviTrustModelEnv,
            environment=request.data.get("environment"),
            trust_model__name="yivi",
        )
        organization = get_object_or_404(Organization, slug=org_slug)
        relying_party = RelyingParty(
            yivi_tme=yivi_tme,
            organization=organization,
            rp_slug=rp_slug,
        )
        relying_party.full_clean()
        relying_party.save()
        return relying_party

    def save_hostname(
        self, request: Any, rp: RelyingParty
    ) -> List[RelyingPartyHostname]:
        hostname_text = request.data.get("hostnames")
        if isinstance(hostname_text, list):
            hostnames = []
            for hostname in hostname_text:
                hostname_obj, _ = RelyingPartyHostname.objects.get_or_create(
                    relying_party=rp,
                    hostname=hostname,
                    defaults={
                        "dns_challenge": generate_dns_challenge(),
                        "dns_challenge_created_at": timezone.now(),
                        "dns_challenge_verified": False,
                    },
                )
                hostname_obj.full_clean()
                hostname_obj.save()
                hostnames.append(hostname_obj)
            return hostnames
        else:
            hostname_obj, _ = RelyingPartyHostname.objects.get_or_create(
                relying_party=rp,
                hostname=hostname_text,
                defaults={
                    "dns_challenge": generate_dns_challenge(),
                    "dns_challenge_created_at": timezone.now(),
                    "dns_challenge_verified": False,
                },
            )
            hostname_obj.full_clean()
            hostname_obj.save()
            return [hostname_obj]

    def save_condiscon(
        self, request: Request, attributes_data: List[Dict[str, str]], rp: RelyingParty
    ) -> Condiscon:
        condiscon_json = self.make_condiscon_from_attributes(attributes_data)
        context_en = request.data.get("context_description_en")
        context_nl = request.data.get("context_description_nl")
        condiscon = Condiscon(
            condiscon=condiscon_json,
            context_description_en=context_en,
            context_description_nl=context_nl,
            relying_party=rp,
        )
        condiscon.full_clean()
        condiscon.save()
        return condiscon

    def save_condiscon_attributes(
        self, condiscon: Condiscon, attributes_data: List[Dict[str, str]]
    ) -> None:
        for attr_data in attributes_data:
            credential_attribute = get_object_or_404(
                CredentialAttribute,
                name=attr_data["credential_attribute_name"],
            )

            condiscon_attr = CondisconAttribute(
                credential_attribute=credential_attribute,
                condiscon=condiscon,
                reason_en=attr_data["reason_en"],
                reason_nl=attr_data["reason_nl"],
            )
            condiscon_attr.full_clean()
            condiscon_attr.save()

    @swagger_auto_schema(
        responses={
            201: "Created",
            404: "Not Found",
            400: "Bad Request",
            401: "Unauthorized",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=[
                "hostname",
                "environment",
                "attributes",
                "context_description_en",
                "context_description_nl",
            ],
            properties={
                "hostname": openapi.Schema(type=openapi.TYPE_STRING),
                "environment": openapi.Schema(type=openapi.TYPE_STRING),
                "context_description_en": openapi.Schema(type=openapi.TYPE_STRING),
                "context_description_nl": openapi.Schema(type=openapi.TYPE_STRING),
                "attributes": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "credential_attribute_id": openapi.Schema(
                                type=openapi.TYPE_INTEGER
                            ),
                            "reason_en": openapi.Schema(type=openapi.TYPE_STRING),
                            "reason_nl": openapi.Schema(type=openapi.TYPE_STRING),
                        },
                    ),
                ),
            },
        ),
    )
    @transaction.atomic
    def post(self, request: Request, org_slug: str) -> Response:
        existing_hostname = check_existing_hostname(request)
        if existing_hostname:
            return existing_hostname

        relying_party = self.save_rp(
            request, org_slug, rp_slug=request.data.get("rp_slug")
        )
        relying_party.ready = False
        relying_party.reviewed_accepted = None
        relying_party.reviewed_at = None
        relying_party.rejection_remarks = None
        relying_party.published_at = None
        relying_party.save()

        hostnames = self.save_hostname(request, relying_party)
        attributes_data = request.data.get("attributes", [])
        condiscon = self.save_condiscon(request, attributes_data, relying_party)
        self.save_condiscon_attributes(condiscon, attributes_data)

        hostname_data = []
        for hostname in hostnames:
            hostname_data.append(
                {"hostname": hostname.hostname, "dns_challenge": hostname.dns_challenge}
            )

        return Response(
            {
                "slug": str(relying_party.rp_slug),
                "message": "Relying party registration successful",
                "hostnames": hostname_data,
                "current_status": {
                    "ready": relying_party.ready,
                    "reviewed_accepted": relying_party.reviewed_accepted,
                    "published_at": relying_party.published_at,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    def get(self, request: Request, org_slug: str):
        organization = get_object_or_404(Organization, slug=org_slug)
        relying_parties = RelyingParty.objects.filter(organization=organization)
        serialized = {
            "relying_parties": [
                {"rp_slug": rp.rp_slug, "environment": rp.yivi_tme.environment}
                for rp in relying_parties
            ]
        }

        return Response(serialized)


class RelyingPartyDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, org_slug, environment, rp_slug):
        relying_party = get_object_or_404(
            RelyingParty,
            organization__slug=org_slug,
            yivi_tme__environment=environment,
            rp_slug=rp_slug,
        )

        hostnames = RelyingPartyHostname.objects.filter(relying_party=relying_party)
        hostnames_data = RelyingPartyHostnameSerializer(hostnames, many=True).data

        condiscon = Condiscon.objects.filter(relying_party=relying_party).first()

        if condiscon:
            condiscon_data = CondisconSerializer(condiscon).data
            condiscon_attributes = CondisconAttribute.objects.filter(
                condiscon=condiscon
            )
            attributes = [
                {
                    "credential_attribute_name": attr.credential_attribute.name,
                    "reason_en": attr.reason_en,
                    "reason_nl": attr.reason_nl,
                }
                for attr in condiscon_attributes
            ]
            context_description_en = condiscon_data.get("context_description_en", "")
            context_description_nl = condiscon_data.get("context_description_nl", "")
        else:
            attributes = []
            context_description_en = ""
            context_description_nl = ""

        serialized = {
            "rp_slug": relying_party.rp_slug,
            "hostnames": hostnames_data,
            "context_description_en": context_description_en,
            "context_description_nl": context_description_nl,
            "attributes": attributes,
            "environment": relying_party.yivi_tme.environment,
            "published_at": relying_party.published_at,
        }
        return Response(serialized, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            204: "No Content",
            404: "Not Found",
            403: "Forbidden",
        }
    )
    @transaction.atomic
    def delete(self, request, environment, org_slug, rp_slug):
        relying_party = get_object_or_404(
            RelyingParty,
            organization__slug=org_slug,
            rp_slug=rp_slug,
            yivi_tme__environment=environment,
        )

        RelyingPartyHostname.objects.filter(relying_party=relying_party).delete()

        condiscons = Condiscon.objects.filter(relying_party=relying_party)
        for condiscon in condiscons:
            CondisconAttribute.objects.filter(condiscon=condiscon).delete()
        condiscons.delete()
        relying_party.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class RelyingPartyUpdateView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        BelongsToOrganization,
        IsMaintainerOrAdmin,
    ]

    def save_updated_rp(
        self,
        request: Request,
        relying_party: RelyingParty,
        response_data: Dict[str, str],
    ) -> Optional[Response]:
        hostnames_raw = request.data.get("hostnames")

        existing_hostname = check_existing_hostname(request)
        if existing_hostname:
            return existing_hostname

        # Normalize: extract `hostname` from each dict
        if isinstance(hostnames_raw, list) and all(
            isinstance(h, dict) and "hostname" in h for h in hostnames_raw
        ):
            hostname_values = [h["hostname"] for h in hostnames_raw]
        elif isinstance(hostnames_raw, dict) and "hostname" in hostnames_raw:
            hostname_values = [hostnames_raw["hostname"]]
        elif isinstance(hostnames_raw, str):
            hostname_values = [hostnames_raw]
        else:
            hostname_values = []

        # Clear existing hostnames and create new ones
        RelyingPartyHostname.objects.filter(relying_party=relying_party).delete()

        hostnames: List[RelyingPartyHostname] = []
        for hostname_text in hostname_values:
            hostname_obj: RelyingPartyHostname = RelyingPartyHostname.objects.create(
                relying_party=relying_party,
                hostname=hostname_text,
                dns_challenge=generate_dns_challenge(),
                dns_challenge_created_at=timezone.now(),
                dns_challenge_verified=False,
            )
            hostnames.append(hostname_obj)

        response_data["hostnames"] = [
            {"hostname": h.hostname, "dns_challenge": h.dns_challenge}
            for h in hostnames
        ]
        response_data["message"] = "Relying party updated successfully"
        return None  # Explicitly return None for clarity

    def save_updated_condiscon(
        self, request: Request, condiscon: Condiscon, relying_party: RelyingParty
    ) -> None:
        if request.data.get("context_description_en") is not None:
            condiscon.context_description_en = request.data.get(
                "context_description_en"
            )
        if request.data.get("context_description_nl") is not None:
            condiscon.context_description_nl = request.data.get(
                "context_description_nl"
            )
        condiscon.save()

    def save_condiscon_attributes(
        self, condiscon: Condiscon, attributes_data: List[Dict[str, str]]
    ) -> None:
        for attr_data in attributes_data:
            credential_attribute = get_object_or_404(
                CredentialAttribute,
                name=attr_data["credential_attribute_name"],
            )

            condiscon_attr = CondisconAttribute(
                credential_attribute=credential_attribute,
                condiscon=condiscon,
                reason_en=attr_data["reason_en"],
                reason_nl=attr_data["reason_nl"],
            )
            condiscon_attr.full_clean()
            condiscon_attr.save()

    def make_condiscon_from_attributes(
        self, attributes_data: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        condiscon_json = {
            "@context": "https://irma.app/ld/request/disclosure/v2",
            "disclose": [[]],
        }

        credential_attributes: Dict[int, List[str]] = {}

        for attr in attributes_data:
            credential_attribute = get_object_or_404(
                CredentialAttribute,
                name=attr["credential_attribute_name"],
            )
            credential_id = credential_attribute.credential.id

            if credential_id not in credential_attributes:
                credential_attributes[credential_id] = []

            credential_attributes[credential_id].append(credential_attribute.name)

        for credential_id, attribute_list in credential_attributes.items():
            condiscon_json["disclose"][0].append(attribute_list)

        return condiscon_json

    @swagger_auto_schema(
        responses={
            200: "Success",
            404: "Not Found",
            400: "Bad Request",
            401: "Unauthorized",
        },
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "hostnames": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "hostname": openapi.Schema(type=openapi.TYPE_STRING)
                        },
                        required=["hostname"],
                    ),
                ),
                "environment": openapi.Schema(type=openapi.TYPE_STRING),
                "context_description_en": openapi.Schema(type=openapi.TYPE_STRING),
                "context_description_nl": openapi.Schema(type=openapi.TYPE_STRING),
                "attributes": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "credential_attribute_name": openapi.Schema(
                                type=openapi.TYPE_STRING
                            ),
                            "reason_en": openapi.Schema(type=openapi.TYPE_STRING),
                            "reason_nl": openapi.Schema(type=openapi.TYPE_STRING),
                        },
                    ),
                ),
                "ready": openapi.Schema(type=openapi.TYPE_BOOLEAN),
            },
        ),
    )
    def patch(self, request: Request, org_slug: str, rp_slug: str) -> Response:
        environment: Optional[str] = request.data.get("environment")
        # TODO: use environment to filter the relying party
        relying_party: RelyingParty = get_object_or_404(
            RelyingParty,
            organization__slug=org_slug,
            rp_slug=rp_slug,
        )
        condiscon: Condiscon = get_object_or_404(Condiscon, relying_party=relying_party)
        response_message: str = "Relying party updated successfully"
        response_data: Dict[str, str] = {"slug": str(relying_party.rp_slug)}

        if (
            request.data.get("context_description_en") is not None
            or request.data.get("context_description_nl") is not None
        ):
            self.save_updated_condiscon(
                request,
                condiscon,
                relying_party,
            )

        if request.data.get("attributes") is not None:
            self.save_updated_attributes(
                request,
                condiscon,
                relying_party,
            )
            attributes_data: List[Dict[str, str]] = request.data.get("attributes")
            condiscon = get_object_or_404(Condiscon, relying_party=relying_party)
            CondisconAttribute.objects.filter(condiscon=condiscon).delete()
            self.save_condiscon_attributes(condiscon, attributes_data)
            condiscon.condiscon = self.make_condiscon_from_attributes(attributes_data)
            condiscon.save()

        if request.data.get("hostnames") is not None:
            self.save_updated_rp(
                request,
                relying_party,
                response_data,
            )

        if request.data.get("environment") is not None:
            yivi_tme: YiviTrustModelEnv = get_object_or_404(
                YiviTrustModelEnv, environment=request.data.get("environment")
            )
            relying_party.yivi_tme = yivi_tme
            relying_party.save()

        if request.data.get("rp_slug") is not None:
            new_slug = request.data.get("rp_slug")
            if new_slug != relying_party.rp_slug:
                relying_party.rp_slug = new_slug
                relying_party.save()
                response_data["rp_slug"] = relying_party.rp_slug
                response_message += ". RP slug updated."

        if "ready" in request.data:
            relying_party.ready = request.data.get("ready")
            relying_party.ready_at = timezone.now() if relying_party.ready else None
            relying_party.reviewed_accepted = None
            relying_party.reviewed_at = None
            relying_party.rejection_remarks = None
            relying_party.published_at = None
            relying_party.save()

        # if any of these fields are updated, set ready to False. User must explicitly set ready to make status PENDING FOR REVIEW
        elif any(
            field in request.data
            for field in [
                "hostname",
                "context_description_en",
                "context_description_nl",
                "attributes",
                "environment",
            ]
        ):
            relying_party.ready = False
            relying_party.ready_at = None
            relying_party.reviewed_accepted = None
            relying_party.reviewed_at = None
            relying_party.rejection_remarks = None
            relying_party.published_at = None
            relying_party.save()

        response_data["message"] = response_message
        return Response(response_data, status=status.HTTP_200_OK)


class RelyingPartyListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request: Request, org_slug: str):
        organization = get_object_or_404(Organization, slug=org_slug)
        relying_parties = RelyingParty.objects.filter(organization=organization)
        serialized = {
            "relying_parties": [
                {"rp_slug": rp.rp_slug, "environment": rp.yivi_tme.environment}
                for rp in relying_parties
            ]
        }

        return Response(serialized)


class RelyingPartyHostnameStatusView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        BelongsToOrganization,
        IsMaintainerOrAdmin,
    ]

    @swagger_auto_schema(responses={200: "Success"})
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
            {
                "hostname": hostname.hostname,
                "dns_challenge": hostname.dns_challenge,
                # hostname can be manually set as verified by admins in admin panel
                "manually_verified": hostname.manually_verified,
                "dns_challenge_verified": hostname.dns_challenge_verified,
                "dns_challenge_verified_at": hostname.dns_challenge_verified_at,
                "dns_challenge_invalidated_at": hostname.dns_challenge_invalidated_at,
            }
        )
