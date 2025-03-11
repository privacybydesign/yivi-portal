from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.shortcuts import get_object_or_404
from ..models.models import *
from django.shortcuts import get_object_or_404
from ..models.model_serializers import *
from rest_framework import permissions


class AttestationProviderListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        responses={200: "Success", 404: "Not Found"}
    )
    def get(self, request, name: str, environment: str):
        """Gets details of a specific attestation provider by ID."""
        attestation_provider = get_object_or_404(AttestationProvider, yivi_tme__trust_model__name=name, yivi_tme__environment=environment)
        serializer = AttestationProviderSerializer(attestation_provider)
        return Response(serializer.data, status=status.HTTP_200_OK)
