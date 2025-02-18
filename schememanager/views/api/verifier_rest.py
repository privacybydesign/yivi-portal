from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from schememanager.serializers import verifier
from schememanager.models.verifier import Verifier
from schememanager.models.organization import Organization
from schememanager.models.scheme import Scheme

class AuthTokenCheck:
    """Middleware to check for a valid token in request headers"""
    pass  # TODO: Implement token authentication middleware

class VerifierListAPIView(AuthTokenCheck, APIView):
    """List verifiers in requestor scheme"""
    permission_classes = [permissions.AllowAny] ## TODO: remove in production

    @swagger_auto_schema(
        operation_description="Retrieve the existing verifiers for a certain email and organization.",
        responses={200: verifier.VerifierSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        verifiers = Verifier.objects.all()
        serializer = verifier.VerifierSerializer(verifiers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        operation_description="Create a verifier instance with organization slug and scheme.",
        request_body=verifier.VerifierSerializer,
        responses={201: verifier.VerifierSerializer(), 400: "Invalid data"}
    )
    def post(self, request, *args, **kwargs):
        serializer = verifier.VerifierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifierDetailAPIView(AuthTokenCheck, APIView):
    """REST API View for retrieving and updating a verifier instance."""

    @swagger_auto_schema(
        operation_description="Retrieve the details of a verifier.",
        responses={200: verifier.VerifierSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        verifier_instance = get_object_or_404(Verifier, organization=request.organization, scheme=request.scheme)
        serializer = verifier.VerifierSerializer(verifier_instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="Update a verifier instance.",
        request_body=verifier.VerifierSerializer,
        responses={200: verifier.VerifierSerializer(), 400: "Invalid data"}
    )
    def post(self, request, *args, **kwargs):
        verifier_instance = get_object_or_404(Verifier, organization=request.organization, scheme=request.scheme)
        serializer = verifier.VerifierSerializer(verifier_instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifierHostnamesAPIView(AuthTokenCheck, APIView):
    """REST API view for getting and posting the hostname."""

    @swagger_auto_schema(
        operation_description="Retrieve the hostname for a verifier.",
        responses={200: openapi.Response("Hostname", openapi.Schema(type=openapi.TYPE_STRING)), 404: "Not found"}
    )
    def get(self, request, *args, **kwargs):
        verifier_hostname = VerifierHostname.objects.filter(organization=request.organization).first()
        if verifier_hostname:
            return Response({"hostname": verifier_hostname.hostname}, status=status.HTTP_200_OK)
        return Response({"error": "Hostname not found"}, status=status.HTTP_404_NOT_FOUND)
