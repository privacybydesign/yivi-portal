from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.response import Response
from portal_backend.models.models import Credential
from portal_backend.models.model_serializers import (
    CredentialSerializer,
)
from rest_framework import permissions


class CredentialListView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request: Request) -> Response:
        credentials = Credential.objects.prefetch_related("attributes").all()
        serializer = CredentialSerializer(credentials, many=True)
        return Response({"credentials": serializer.data})
