from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from portal_backend.models.models import Credential
from portal_backend.models.model_serializers import (
    CredentialListSerializer,
)
from rest_framework import permissions, status
from silk.profiling.profiler import silk_profile


class CredentialListView(APIView):
    permission_classes = [permissions.AllowAny]

    @silk_profile(name="CredentialListView.get")
    def get(self, request: Request) -> Response:
        credentials = (
            Credential.objects.select_related(
                "attestation_provider__yivi_tme",
                "attestation_provider__organization",
            )
            .prefetch_related("attributes")
            .filter(deprecated_since__isnull=True)
        )
        serializer = CredentialListSerializer(credentials, many=True)
        return Response({"credentials": serializer.data})


class CredentialsListViewWithDeprecated(APIView):
    permission_classes = [permissions.AllowAny]

    """
    This view returns all credentials for the attribute index page, including deprecated ones.
    """

    @silk_profile(name="CredentialsListViewWithDeprecated.get")
    def get(
        self,
        request: Request,
    ) -> Response:

        credentials = (
            Credential.objects.select_related(
                "attestation_provider",
                "attestation_provider__organization",
                "attestation_provider__yivi_tme",
            )
            .prefetch_related("attributes")
            .order_by("name_en")
        )
        serializer = CredentialListSerializer(credentials, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
