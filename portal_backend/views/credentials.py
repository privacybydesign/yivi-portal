from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from portal_backend.models.models import Credential
from portal_backend.models.model_serializers import (
    CredentialListSerializer,
)
from rest_framework import status
from rest_framework import permissions


class CredentialListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request: Request) -> Response:
        credentials = (
            Credential.objects.select_related(
                "attestation_provider__yivi_tme",
                "attestation_provider__organization",
            )
            .prefetch_related("attributes")
            .all()
        )
        serializer = CredentialListSerializer(credentials, many=True)
        return Response({"credentials": serializer.data})
