import logging
from typing import Optional
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema  # type: ignore
from rest_framework import status
from portal_backend.services.organizaion import filter_organizations
from ..models.model_serializers import MaintainerSerializer, OrganizationSerializer
from ..models.models import Organization
from rest_framework import permissions
from rest_framework.parsers import FormParser, MultiPartParser
from ..models.models import User
from rest_framework.pagination import LimitOffsetPagination
from .permissions import IsOrganizationMaintainerOrAdmin
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.request import Request
from ..swagger_specs.organization import (
    organization_create_schema,
    organization_update_schema,
    organization_maintainer_create_schama,
    organization_maintainer_delete_schema,
)

logger = logging.getLogger(__name__)


class OrganizationCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @organization_create_schema
    @transaction.atomic
    def post(self, request: Request) -> Response:
        """Creates an organization."""

        email = request.user.email
        serializer = OrganizationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            organization = serializer.save()
            User.objects.create(
                email=email, organization=organization, role="maintainer"
            )
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return Response(
                {"error": "Failed to create user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"success": f"Created organization with ID {organization.id} for {email}"},
            status=status.HTTP_201_CREATED,
        )


class OrganizationListView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={200: "Success", 404: "Not Found"})
    def get(self, request: Request) -> Response:
        """Get all registered organizations"""

        logger.info("Fetching all registered organizations")

        orgs = filter_organizations(request)
        paginator = LimitOffsetPagination()
        paginator.default_limit = 20
        result_page = paginator.paginate_queryset(orgs, request)
        serializer = OrganizationSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)


class OrganizationDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={200: "Success", 404: "Not Found"})
    def get(self, request: Request, org_slug: str) -> Response:
        """Get organization by uuid"""
        logger.info("Fetching organization with slug: %s", org_slug)

        org = get_object_or_404(Organization, slug=org_slug)
        serializer = OrganizationSerializer(org)
        return Response(serializer.data)


class OrganizationUpdateView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsOrganizationMaintainerOrAdmin,
    ]
    parser_classes = [MultiPartParser, FormParser]

    @organization_update_schema
    def patch(self, request: Request, org_slug: str) -> Response:
        """Updates an organization, given the uuid."""
        organization = get_object_or_404(Organization, slug=org_slug)
        serializer = OrganizationSerializer(
            organization,
            data=request.data,
            partial=True,
        )
        if not serializer.is_valid():
            logger.error(f"Validation errors: {serializer.errors}")
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class OrganizationMaintainersView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsOrganizationMaintainerOrAdmin,
    ]

    @swagger_auto_schema(responses={200: "Success"})
    def get(self, request: Request, org_slug: str) -> Response:
        """Get all maintainers for an organization"""
        organization = get_object_or_404(Organization, slug=org_slug)
        maintainers = User.objects.filter(organization=organization)
        serializer = MaintainerSerializer(maintainers, many=True)
        return Response(serializer.data)

    @organization_maintainer_create_schama
    def post(self, request: Request, org_slug: str) -> Response:
        """Add a maintainer to an organization"""
        organization = get_object_or_404(Organization, slug=org_slug)
        email: Optional[str] = request.data.get("email")

        if not email:
            return Response(
                {"email": "Email is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        existing_user = User.objects.filter(
            email=email, organization=organization
        ).first()
        if existing_user:
            return Response(
                {
                    "email": f"User with email {email} is already a maintainer of this organization"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        User.objects.create(email=email, organization=organization, role="maintainer")

        return Response(
            {"message": f"User {email} added to organization as maintainer"},
            status=status.HTTP_201_CREATED,
        )


class OrganizationMaintainerView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        IsOrganizationMaintainerOrAdmin,
    ]

    @organization_maintainer_delete_schema
    def delete(self, request: Request, org_slug: str, maintainer_id: str) -> Response:
        """Remove a maintainer from an organization"""

        if not maintainer_id:
            return Response(
                {"error": "Maintainer id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        maintainer = get_object_or_404(User, pk=maintainer_id)

        if maintainer.email == request.user.email:
            return Response(
                {"error": "Cannot remove yourself from the organization"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        organization = get_object_or_404(Organization, slug=org_slug)
        deleted, _ = User.objects.filter(
            pk=maintainer_id, organization=organization
        ).delete()

        if deleted:
            return Response(
                {"message": "User removed from organization"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "User is not a maintainer of this organization"},
                status=status.HTTP_404_NOT_FOUND,
            )
