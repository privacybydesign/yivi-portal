import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema  # type: ignore
from rest_framework import status
from ..models.model_serializers import OrganizationSerializer
from ..models.models import Organization
from rest_framework import permissions
from ..models.models import User
from .helpers import BelongsToOrganization, IsMaintainer
from rest_framework.pagination import LimitOffsetPagination
from drf_yasg import openapi  # type: ignore
from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)


class OrganizationListAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={200: "Success"})
    def get(self, request):
        """Get all registered organizations"""

        logger.info("Fetching all registered organizations")

        orgs = Organization.objects.filter(is_verified=True)
        paginator = LimitOffsetPagination()
        paginator.default_limit = 10
        result_page = paginator.paginate_queryset(orgs, request)
        serializer = OrganizationSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        request_body=OrganizationSerializer,
        responses={201: "Success", 400: "Bad Request"},
    )
    def post(self, request):
        """Creates an organization."""

        logger.info("Creating a new organization")

        serializer = OrganizationSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning("Invalid organization data: %s", serializer.errors)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        organization = serializer.save()
        logger.info("Organization created with ID: %s", organization.id)
        return Response({"id": organization.id}, status=status.HTTP_201_CREATED)


class OrganizationDetailAPIView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={200: "Success"})
    def get(self, request, pk):
        """Get organization by uuid"""
        logger.info("Fetching organization with ID: %s", pk)

        org = Organization.objects.get(pk=pk)
        serializer = OrganizationSerializer(org)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=OrganizationSerializer,
        responses={201: "Success", 400: "Bad Request", 404: "Not Found"},
    )
    def patch(self, request, pk):
        """Updates an organization, given the uuid."""
        organization = get_object_or_404(Organization, pk=pk)
        serializer = OrganizationSerializer(
            organization, data=request.data, partial=True
        )
        if not serializer.is_valid():
            return Response(
                {"Your Organization registration was updated.", serializer.data},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class OrganizationMaintainersAPIView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        BelongsToOrganization,
        IsMaintainer,
    ]

    @swagger_auto_schema(responses={200: "Success"})
    def get(self, request, pk):
        """Get all maintainers for an organization"""
        organization = get_object_or_404(Organization, pk=pk)
        maintainers = User.objects.filter(organization=organization)

        return Response(
            {
                "maintainers": [
                    {
                        "email": user.email,
                    }
                    for user in maintainers
                ]
            }
        )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email"],
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
                ),
            },
        ),
        responses={
            201: "Created",
            400: "Bad Request",
            403: "Forbidden - Not enough permissions",
            404: "Organization not found",
        },
    )
    def post(self, request, pk):
        """Add a maintainer to an organization"""
        organization = get_object_or_404(Organization, pk=pk)

        email = request.data.get("email")

        if not email:
            return Response(
                {"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        existing_user = User.objects.filter(
            email=email, organization=organization
        ).first()
        if existing_user:
            return Response(
                {
                    "error": f"User with email {email} is already a maintainer of this organization"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        User.objects.create(email=email, organization=organization, role="maintainer")

        return Response(
            {"message": f"User {email} added to organization as maintainer"},
            status=status.HTTP_201_CREATED,
        )

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email"],
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL
                ),
            },
        ),
        responses={
            200: "Success",
            400: "Bad Request",
            403: "Forbidden",
            404: "Not Found",
        },
    )
    def delete(self, request, pk):
        """Remove a maintainer from an organization"""
        email = request.data.get("email")

        if not email:
            return Response(
                {"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        if email == request.user.email:
            return Response(
                {"error": "Cannot remove yourself from the organization"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        organization = get_object_or_404(Organization, pk=pk)
        deleted, _ = User.objects.filter(
            email=email, organization=organization
        ).delete()

        if deleted:
            return Response(
                {"message": f"User {email} removed from organization"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {
                    "error": f"User with email {email} is not a maintainer of this organization"
                },
                status=status.HTTP_404_NOT_FOUND,
            )
