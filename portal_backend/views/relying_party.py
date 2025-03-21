from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema  # type: ignore
from drf_yasg import openapi  # type: ignore
from ..models.models import (
    RelyingParty,
    RelyingPartyHostname,
    YiviTrustModelEnv,
    Organization,
    Condiscon,
    CondisconAttribute,
    CredentialAttribute,
    Status,
)
from django.shortcuts import get_object_or_404
from ..models.model_serializers import RelyingPartySerializer
from rest_framework import permissions
from django.utils import timezone
from django.db import transaction
from ..dns_verification import generate_dns_challenge
from .helpers import IsMaintainer, BelongsToOrganization


def check_existing_hostname(request):
    hostname_data = request.data.get("hostname")
    # check if hostname_data is a list
    if isinstance(hostname_data, list):
        for hostname in hostname_data:
            if RelyingPartyHostname.objects.filter(hostname=hostname).exists():
                return Response(
                    {
                        "error": f"Hostname '{hostname}' is already registered by another relying party"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
    else:
        if RelyingPartyHostname.objects.filter(hostname=hostname_data).exists():
            return Response(
                {
                    "error": "This hostname is already registered by another relying party"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class RelyingPartyDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={200: "Success", 404: "Not Found"})
    def get(self, request, trustmodel_name: str, environment: str, org_slug: str):
        """Gets details of a specific relying party."""
        relying_party = get_object_or_404(
            RelyingParty,
            yivi_tme__trust_model__name__iexact=trustmodel_name,
            yivi_tme__environment=environment,
            organization__slug=org_slug,
        )

        base_data = RelyingPartySerializer(relying_party).data

        hostname = RelyingPartyHostname.objects.filter(
            relying_party=relying_party
        ).first()
        condiscon = Condiscon.objects.filter(relying_party=relying_party).first()

        response_data = {
            **base_data,
            "hostname_data": (
                {
                    "hostname": hostname.hostname if hostname else None,
                    "dns_challenge": hostname.dns_challenge if hostname else None,
                    "dns_verified": (
                        hostname.dns_challenge_verified if hostname else None
                    ),
                }
                if hostname
                else None
            ),
            "condiscon_data": (
                {
                    "context_description_en": (
                        condiscon.context_description_en if condiscon else None
                    ),
                    "context_description_nl": (
                        condiscon.context_description_nl if condiscon else None
                    ),
                    "condiscon": condiscon.condiscon if condiscon else None,
                }
                if condiscon
                else None
            ),
        }

        return Response(response_data, status=status.HTTP_200_OK)


class RelyingPartyRegisterView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        BelongsToOrganization,
        IsMaintainer,
    ]

    def make_condiscon_from_attributes(self, attributes_data):
        """
        Generate a condiscon JSON structure from attribute data
        """
        condiscon_json = {
            "@context": "https://irma.app/ld/request/disclosure/v2",
            "disclose": [[]],
        }

        credential_attributes = {}

        for attr in attributes_data:
            credential_attribute = CredentialAttribute.objects.get(
                credential__credential_tag=attr["credential_attribute_tag"],
                name=attr["credential_attribute_name"],
            )
            credential_id = credential_attribute.credential.id

            if credential_id not in credential_attributes:
                credential_attributes[credential_id] = []

            credential_attributes[credential_id].append(credential_attribute.name)

        for credential_id, attribute_list in credential_attributes.items():
            condiscon_json["disclose"][0].append(attribute_list)

        return condiscon_json

    def save_rp(self, request, org_slug):
        yivi_tme = get_object_or_404(
            YiviTrustModelEnv, environment=request.data.get("trust_model_env")
        )
        organization = get_object_or_404(Organization, slug=org_slug)
        relying_party = RelyingParty(
            yivi_tme=yivi_tme,
            organization=organization,
        )
        relying_party.full_clean()
        relying_party.save()
        return relying_party

    def save_hostname(self, request, rp):
        hostname_text = request.data.get("hostname")
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

    def save_condiscon(self, request, attributes_data, rp):
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

    def save_condiscon_attributes(self, condiscon, attributes_data):
        for attr_data in attributes_data:
            credential_attribute = get_object_or_404(
                CredentialAttribute,
                credential__credential_tag=attr_data["credential_attribute_tag"],
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

    def check_existing_rp(self, request, org_slug):
        if RelyingParty.objects.filter(organization__slug=org_slug).exists():
            return Response(
                {"error": "The organization already has a relying party registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )

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
                "trust_model_env",
                "attributes",
                "context_description_en",
                "context_description_nl",
            ],
            properties={
                "hostname": openapi.Schema(type=openapi.TYPE_STRING),
                "trust_model_env": openapi.Schema(type=openapi.TYPE_STRING),
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
    def post(self, request, org_slug):
        existing_rp = self.check_existing_rp(request, org_slug)
        if existing_rp:
            return existing_rp
        existing_hostname = check_existing_hostname(request)
        if existing_hostname:
            return existing_hostname

        relying_party = self.save_rp(request, org_slug)
        rp_status = Status.objects.get(relying_party=relying_party).rp_status
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
                "id": str(relying_party.id),
                "message": "Relying party registration successful",
                "hostnames": hostname_data,
                "current_status": rp_status,
            },
            status=status.HTTP_201_CREATED,
        )


class RelyingPartyDetailView(APIView):

    def patch(self, request, pk, environment, slug):
        relying_party = get_object_or_404(
            RelyingParty,
            organization__id=pk,
            yivi_tme__environment=environment,
            organization__slug=slug,
        )
        response_message = "Relying party updated successfully"
        response_data = {"id": str(relying_party.id)}

        if request.data.get("hostname") is not None:
            hostname_data = request.data.get("hostname")

            existing_hostname = check_existing_hostname(request)
            if existing_hostname:
                return existing_hostname

            if isinstance(hostname_data, list):
                # delete existing hostnames
                RelyingPartyHostname.objects.filter(
                    relying_party=relying_party
                ).delete()

                # create new hostnames
                hostnames = []
                for hostname_text in hostname_data:
                    hostname_obj = RelyingPartyHostname.objects.create(
                        relying_party=relying_party,
                        hostname=hostname_text,
                        dns_challenge=generate_dns_challenge(),
                        dns_challenge_created_at=timezone.now(),
                        dns_challenge_verified=False,
                    )
                    hostnames.append(hostname_obj)

                hostname_data_response = []
                for hostname in hostnames:
                    hostname_data_response.append(
                        {
                            "hostname": hostname.hostname,
                            "dns_challenge": hostname.dns_challenge,
                        }
                    )

                response_data["hostnames"] = hostname_data_response
                response_message += ". Hostnames updated. Please update your DNS records with the new challenges."
            else:
                hostname_obj = RelyingPartyHostname.objects.filter(
                    relying_party=relying_party
                ).first()

                if hostname_obj:
                    if hostname_obj.hostname != hostname_data:
                        hostname_obj.hostname = hostname_data
                        hostname_obj.dns_challenge = generate_dns_challenge()
                        hostname_obj.dns_challenge_created_at = timezone.now()
                        hostname_obj.dns_challenge_verified = False
                        hostname_obj.dns_challenge_verified_at = None
                        hostname_obj.save()
                        response_data["hostname"] = hostname_obj.hostname
                        response_data["dns_challenge"] = hostname_obj.dns_challenge
                        response_message += ". Hostname updated. Please update your DNS record with the new challenge."
                else:
                    hostname_obj = RelyingPartyHostname.objects.create(
                        relying_party=relying_party,
                        hostname=hostname_data,
                        dns_challenge=generate_dns_challenge(),
                        dns_challenge_created_at=timezone.now(),
                        dns_challenge_verified=False,
                    )
                    response_data["hostname"] = hostname_obj.hostname
                    response_data["dns_challenge"] = hostname_obj.dns_challenge
                    response_message += (
                        ". Hostname added. Please add a DNS record with the challenge."
                    )

            if (
                request.data.get("context_description_en") is not None
                or request.data.get("context_description_nl") is not None
            ):
                condiscon = get_object_or_404(Condiscon, relying_party=relying_party)
                if request.data.get("context_description_en") is not None:
                    condiscon.context_description_en = request.data.get(
                        "context_description_en"
                    )
                if request.data.get("context_description_nl") is not None:
                    condiscon.context_description_nl = request.data.get(
                        "context_description_nl"
                    )
                condiscon.save()

            if request.data.get("attributes") is not None:
                attributes_data = request.data.get("attributes")
                condiscon = get_object_or_404(Condiscon, relying_party=relying_party)
                CondisconAttribute.objects.filter(condiscon=condiscon).delete()
                self.save_condiscon_attributes(condiscon, attributes_data)
                condiscon.condiscon = self.make_condiscon_from_attributes(
                    attributes_data
                )
                condiscon.save()

            if request.data.get("trust_model_env") is not None:
                yivi_tme = get_object_or_404(
                    YiviTrustModelEnv, environment=request.data.get("trust_model_env")
                )
                relying_party.yivi_tme = yivi_tme
                relying_party.save()

            if "ready" in request.data:
                rp_status = Status.objects.get(relying_party=relying_party)
                rp_status.ready = request.data.get("ready")
                rp_status.ready_at = (
                    timezone.now() if request.data.get("ready") else None
                )
                rp_status.save()

            # if any of these fields are updated, set ready to False. User must explicitly set ready to make status PENDING FOR REVIEW
            elif any(
                field in request.data
                for field in [
                    "hostname",
                    "context_description_en",
                    "context_description_nl",
                    "attributes",
                    "trust_model_env",
                ]
            ):
                rp_status = Status.objects.get(relying_party=relying_party)
                rp_status.ready = False
                rp_status.save()

            response_data["message"] = response_message
            return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            204: "No Content",
            404: "Not Found",
            403: "Forbidden",
        }
    )
    @transaction.atomic
    def delete(self, request, pk):
        relying_party = get_object_or_404(RelyingParty, organization__id=pk)

        RelyingPartyHostname.objects.filter(relying_party=relying_party).delete()

        condiscons = Condiscon.objects.filter(relying_party=relying_party)
        for condiscon in condiscons:
            CondisconAttribute.objects.filter(condiscon=condiscon).delete()
        condiscons.delete()

        Status.objects.filter(relying_party=relying_party).delete()

        relying_party.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class RelyingPartyHostnameStatusView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        BelongsToOrganization,
        IsMaintainer,
    ]

    @swagger_auto_schema(responses={200: "Success"})
    def get(self, request, slug):
        """Get status of DNS verification for a hostname"""
        relying_party = get_object_or_404(RelyingParty, organization__slug=slug)
        hostname = get_object_or_404(RelyingPartyHostname, relying_party=relying_party)

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


class RelyingPartyRegistrationStatusView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        BelongsToOrganization,
        IsMaintainer,
    ]

    @swagger_auto_schema(responses={200: "Success"})
    def get(self, request, slug):
        """Get status of relying party registration"""
        relying_party = get_object_or_404(RelyingParty, organization__slug=slug)
        status = get_object_or_404(Status, relying_party=relying_party)

        return Response(
            {
                "current_status": status.rp_status.label,
                "ready": status.ready,
                "ready_at": status.ready_at,
            }
        )
