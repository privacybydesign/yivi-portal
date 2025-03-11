from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema  # type: ignore
from ..models.models import *
from django.shortcuts import get_object_or_404
from ..models.model_serializers import *

from rest_framework import permissions


class TrustModelListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        responses={200: "Success"}
    )
    def get(self, request):
        """Gets a list of trust models."""
        trust_models = TrustModel.objects.all()
        serializer = TrustModelSerializer(trust_models, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TrustModelDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        responses={200: "Success",
                   404: "Not found"}
    )
    def get(self, request, name: str):
        """Gets a specific trust model."""
        trust_model = get_object_or_404(TrustModel, name=name)
        serializer = TrustModelSerializer(trust_model)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TrustModelEnvironments(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        responses={200: "Success",
                   404: "Not found"}
    )
    def get(self, request, name: str):
        """Gets a list of environments for a trust model."""
        trust_model = get_object_or_404(TrustModel, name=name)
        environments = trust_model.environments.all()
        serializer = YiviTrustModelEnvSerializer(environments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TrustModelEnvironment(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        responses={200: "Success",
                   404: "Not found"}
    )
    def get(self, request, name: str, environment: str):
        """Gets a list of environments for a trust model."""
        trust_model = get_object_or_404(TrustModel, name=name)
        environments = trust_model.environments.all()
        serializer = YiviTrustModelEnvSerializer(environments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
