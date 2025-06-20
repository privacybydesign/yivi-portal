from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema  # type: ignore
from ..models.models import TrustModel
from django.shortcuts import get_object_or_404
from ..models.model_serializers import TrustModelSerializer, YiviTrustModelEnvSerializer
from rest_framework import permissions
from silk.profiling.profiler import silk_profile


class TrustModelListView(APIView):
    permission_classes = [permissions.AllowAny]

    @silk_profile(name="TrustModelListView.get")
    @swagger_auto_schema(responses={200: "Success"})
    def get(self, request: Request) -> Response:
        """Gets a list of trust models."""
        trust_models = TrustModel.objects.all()
        serializer = TrustModelSerializer(trust_models, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TrustModelDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    @silk_profile(name="TrustModelDetailView.get")
    @swagger_auto_schema(responses={200: "Success", 404: "Not found"})
    def get(self, request: Request, name: str) -> Response:
        """Gets a specific trust model."""
        trust_model = get_object_or_404(TrustModel, name=name)
        serializer = TrustModelSerializer(trust_model)
        return Response(serializer.data, status=status.HTTP_200_OK)


class YiviTrustModelEnvListView(APIView):
    permission_classes = [permissions.AllowAny]

    @silk_profile(name="YiviTrustModelEnvListView.get")
    @swagger_auto_schema(responses={200: "Success", 404: "Not found"})
    def get(self, request: Request, trust_model_name: str) -> Response:
        """Gets a list of environments for a trust model."""
        trust_model = get_object_or_404(TrustModel, name__iexact=trust_model_name)
        environments = trust_model.environments.all()
        serializer = YiviTrustModelEnvSerializer(environments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
