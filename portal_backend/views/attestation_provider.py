from django.shortcuts import get_object_or_404
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema  # type: ignore
from portal_backend.models.models import AttestationProvider, Organization
from portal_backend.models.model_serializers import (
    AttestationProviderSerializer,
)
from rest_framework import permissions
from silk.profiling.profiler import silk_profile


class AttestationProviderListView(APIView):
    permission_classes = [permissions.AllowAny]

    @silk_profile(name="AttestationProviderListView.get")
    def get(self, request: Request, org_slug: str) -> Response:
        organization = get_object_or_404(Organization, slug=org_slug)
        attestation_providers = AttestationProvider.objects.filter(
            organization=organization
        )
        return Response(
            {
                "attestation_providers": [
                    {
                        "ap_slug": ap.ap_slug,
                        "environment": ap.yivi_tme.environment,
                        "status": ap.status,
                    }
                    for ap in attestation_providers
                ]
            }
        )


class AttestationProviderRetrieveView(APIView):
    permission_classes = [permissions.AllowAny]

    @silk_profile(name="AttestationProviderRetrieveView.get")
    @swagger_auto_schema(responses={200: "Success", 404: "Not Found"})
    def get(
        self,
        request,
        org_slug: str,
        environment: str,
        ap_slug: str,
    ):
        """Gets details of a specific attestation provider by ID."""
        try:
            attestation_provider = AttestationProvider.objects.get(
                organization__slug=org_slug,
                ap_slug=ap_slug,
                yivi_tme__environment=environment,
            )
            ap_credentials = attestation_provider.credentials.all()
        except AttestationProvider.DoesNotExist:
            return Response(
                {"detail": "Attestation provider not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = AttestationProviderSerializer(attestation_provider)
        all_credentials = [
            {
                "id": credential.id,
                "name_en": credential.name_en,
                "credential_id": credential.credential_id,
                "description_en": credential.description_en,
                "full_path": credential.full_path,
                "deprecated_since": credential.deprecated_since,
                "attributes": [
                    {
                        "id": attr.id,
                        "name_en": attr.name_en,
                        "description_en": attr.description_en,
                        "full_path": attr.full_path,
                    }
                    for attr in credential.attributes.all()
                ],
            }
            for credential in ap_credentials
        ]

        response = serializer.data
        response["credentials"] = all_credentials

        return Response(response, status=status.HTTP_200_OK)


class AttestationProviderCredentialsListView(APIView):
    """
    List of all the credentials for a specific attestation provider"""

    @silk_profile(name="AttestationProviderCredentialsListView.get")
    def get(
        self,
        request: Request,
        org_slug: str,
        environment: str,
        ap_slug: str,
    ) -> Response:
        attestation_provider = AttestationProvider.objects.get(
            organization__slug=org_slug,
            ap_slug=ap_slug,
            yivi_tme__environment=environment,
        )
        credentials = attestation_provider.credentials.all()
        serializer = AttestationProviderSerializer(credentials, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
