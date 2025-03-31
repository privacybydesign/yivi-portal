from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema  # type: ignore
from django.shortcuts import get_object_or_404
from portal_backend.models.models import AttestationProvider
from portal_backend.models.model_serializers import AttestationProviderSerializer
from rest_framework import permissions


class AttestationProviderListView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={200: "Success", 404: "Not Found"})
    def get(self, request, trustmodel_name: str, environment: str):
        """Gets details of a specific attestation provider by ID."""
        attestation_providers = AttestationProvider.objects.filter(
            yivi_tme__trust_model__name=trustmodel_name,
            yivi_tme__environment=environment,
        )
        if not attestation_providers.exists():
            return Response(
                {"detail": "Attestation provider not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = AttestationProviderSerializer(attestation_providers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
