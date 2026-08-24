import logging
from typing import ClassVar

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from drf_yasg.utils import swagger_auto_schema  # type: ignore
from rest_framework import permissions, status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from portal_backend.services.organization import filter_organizations

from ..models.model_serializers import MaintainerSerializer, OrganizationSerializer
from ..models.models import Organization, User
from ..swagger_specs.organization import (
    organization_create_schema,
    organization_maintainer_create_schama,
    organization_maintainer_delete_schema,
    organization_update_schema,
)
from .permissions import IsOrganizationMaintainerOrAdmin

logger = logging.getLogger(__name__)


class OrganizationCreateView(APIView):
    permission_classes: ClassVar[list] = [permissions.IsAuthenticated]
    parser_classes: ClassVar[list] = [MultiPartParser, FormParser]

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
            user, _ = User.objects.get_or_create(
                email=email, defaults={"role": "maintainer"}
            )
            user.organizations.add(organization)

        except Exception as e:  # noqa: BLE001
            transaction.set_rollback(True)
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
    permission_classes: ClassVar[list] = [permissions.AllowAny]

    @swagger_auto_schema(responses={200: "Success", 404: "Not Found"})
    def get(self, request: Request) -> Response:
        """Get all registered organizations"""

        orgs = filter_organizations(request)
        paginator = LimitOffsetPagination()
        paginator.default_limit = 20
        result_page = paginator.paginate_queryset(orgs, request)
        serializer = OrganizationSerializer(
            result_page, many=True, context={"request": request}
        )
        return paginator.get_paginated_response(serializer.data)


class OrganizationDetailView(APIView):
    permission_classes: ClassVar[list] = [permissions.AllowAny]

    @swagger_auto_schema(responses={200: "Success", 404: "Not Found"})
    def get(self, request: Request, org_slug: str) -> Response:
        """Get organization by uuid"""

        org = Organization.objects.with_role_annotations().filter(slug=org_slug)

        if (
            request.user.is_authenticated
            and IsOrganizationMaintainerOrAdmin().has_permission(request, self)
        ):
            org = org.first()
        else:
            org = org.exclude(is_verified=False).first()

        logger.info(f"Fetching organization with slug: {org_slug}")
        if not org:
            return Response(
                {"error": "Organization not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = OrganizationSerializer(org, context={"request": request})
        return Response(serializer.data)


class OrganizationUpdateView(APIView):
    permission_classes: ClassVar[list] = [
        permissions.IsAuthenticated,
        IsOrganizationMaintainerOrAdmin,
    ]
    parser_classes: ClassVar[list] = [MultiPartParser, FormParser]

    @organization_update_schema
    # @transaction.atomic
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
        try:
            serializer.save()
        except Exception as e:  # noqa: BLE001
            logger.error(f"Error saving to database: {e}")
            return Response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(status=status.HTTP_200_OK)


class OrganizationMaintainersView(APIView):
    permission_classes: ClassVar[list] = [
        permissions.IsAuthenticated,
        IsOrganizationMaintainerOrAdmin,
    ]

    @swagger_auto_schema(responses={200: "Success"})
    def get(self, request: Request, org_slug: str) -> Response:
        """Get all maintainers for an organization"""
        organization = get_object_or_404(Organization, slug=org_slug)
        maintainers = User.objects.filter(organizations=organization).distinct()
        serializer = MaintainerSerializer(maintainers, many=True)
        return Response(serializer.data)

    @organization_maintainer_create_schama
    @transaction.atomic
    def post(self, request: Request, org_slug: str) -> Response:
        """Add a maintainer to an organization"""
        organization = get_object_or_404(Organization, slug=org_slug)
        email: str | None = request.data.get("email")

        if not email:
            return Response(
                {"email": "Email is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not organization.is_verified:
            return Response(
                {
                    "error": "Cannot add maintainers to an unverified organization. Wait for verification."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            user = User.objects.prefetch_related("organizations").get(email=email)
            if user and organization in user.organizations.all():
                return Response(
                    {
                        "email": f"User with email {email} is already a maintainer of this organization"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        except User.DoesNotExist:
            user = User(email=email, role="maintainer")
            try:
                user.full_clean()
                user.save()

            except ValidationError as e:
                transaction.set_rollback(True)
                logger.error(f"Validation error creating user: {e}")
                return Response(
                    {"error": e.message_dict},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            except Exception as e:  # noqa: BLE001
                transaction.set_rollback(True)
                logger.error(f"Unexpected error creating user: {e}")
                return Response(
                    {"error": "Failed to create user"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            user.organizations.add(organization)

        # Send email notification to the maintainer that was just added
        try:

            html_content = render_to_string(
                "email-template.html",
                {
                    "added_by": request.user.email,
                    "organization_name": organization.name_en,
                    "portal_url": "https://" + settings.YIVI_PORTAL_URL,
                },
            )

            email_notification = EmailMessage(
                "Yivi Portal - You have been added as a maintainer",
                html_content,
                settings.EMAIL_FROM,
                [email],
            )
            email_notification.content_subtype = "html"
            email_notification.send()
        except Exception:
            transaction.set_rollback(True)
            logger.exception("Failed to send email notification")
            return Response(
                {"error": "Failed to send email notification."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {"message": f"User {email} added to organization as maintainer"},
            status=status.HTTP_201_CREATED,
        )


class OrganizationMaintainerView(APIView):
    permission_classes: ClassVar[list] = [
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
        maintainer = get_object_or_404(User, public_id=maintainer_id)

        if maintainer.email == request.user.email:
            return Response(
                {"error": "Cannot remove yourself from the organization"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        organization = get_object_or_404(Organization, slug=org_slug)
        deleted, _ = User.objects.filter(
            public_id=maintainer_id, organizations=organization
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


class OrganizationNameAndSlugView(APIView):
    permission_classes: ClassVar[list] = [permissions.IsAuthenticated]

    @swagger_auto_schema(responses={200: "Success", 404: "Not Found"})
    def get(self, request: Request) -> Response:
        """Get all of maintainer's organizations' names and slugs to display in the dropdown"""

        user = User.objects.filter(email=request.user.email).first()
        orgs = user.organizations.all()

        return Response(
            [
                {
                    "name_en": org.name_en,
                    "slug": org.slug,
                }
                for org in orgs
            ],
            status=status.HTTP_200_OK,
        )
