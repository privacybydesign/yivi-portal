from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from ..models.models import *
from django.shortcuts import get_object_or_404
from ..models.model_serializers import *
from rest_framework import permissions


class AttestationProviderListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        responses={200: "Success", 404: "Not Found"}
    )
    def get(self, request, environment):
        """Gets details of a specific attestation provider by ID."""
        attestation_provider = AttestationProvider.objects.get(yivi_tme__environment=environment)
        serializer = AttestationProviderSerializer(attestation_provider)
        return Response(serializer.data, status=status.HTTP_200_OK)
