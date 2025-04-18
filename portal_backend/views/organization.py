import logging
from typing import Optional
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema  # type: ignore
from rest_framework import status
from ..models.model_serializers import MaintainerSerializer, OrganizationSerializer
from ..models.models import AttestationProvider, Organization, RelyingParty, TrustModel
from rest_framework import permissions
from ..models.models import User
from .helpers import BelongsToOrganization, IsMaintainerOrAdmin
from rest_framework.pagination import LimitOffsetPagination
from drf_yasg import openapi  # type: ignore
from django.shortcuts import get_object_or_404
from django.db.models import Exists, OuterRef, Q
from django.db import transaction
from rest_framework.request import Request

logger = logging.getLogger(__name__)


def to_nullable_bool(value: Optional[str]) -> Optional[bool]:
    if value is None:
        return None
    value = value.lower()
    if value == "true":
        return True
    if value == "false":
        return False
    return None


class OrganizationListView(APIView):
    permission_class = permissions.AllowAny

    @swagger_auto_schema(responses={200: "Success"})
    def get(self, request: Request) -> Response:
        """Get all registered organizations"""

        logger.info("Fetching all registered organizations")

        search_query: Optional[str] = request.query_params.get("search")
        trust_model: Optional[str] = request.query_params.get("trust_model")
        select_aps: Optional[bool] = to_nullable_bool(request.query_params.get("ap"))
        select_rps: Optional[bool] = to_nullable_bool(request.query_params.get("rp"))

        # If both select_aps and select_rps are False, return an empty list
        if select_aps is False and select_rps is False:
            paginator = LimitOffsetPagination()
            paginator.default_limit = 20
            result_page = paginator.paginate_queryset([], request)
            serializer = OrganizationSerializer(result_page, many=True)
            return paginator.get_paginated_response(serializer.data)

        orgs = (
            Organization.objects.annotate(
                is_rp=Exists(RelyingParty.objects.filter(organization=OuterRef("pk"))),
                is_ap=Exists(
                    AttestationProvider.objects.filter(organization=OuterRef("pk"))
                ),
            )
            .filter(is_verified=True)
            .filter(
                (Q(is_rp=select_rps) if select_rps is not None else Q())
                | (Q(is_ap=select_aps) if select_aps is not None else Q())
            )
            .order_by("name_en")
        )

        if search_query:
            orgs = orgs.filter(name_en__icontains=search_query) | orgs.filter(
                name_en__icontains=search_query
            )
        if trust_model:
            orgs = Organization.objects.filter(trust_models__name=trust_model)

        paginator = LimitOffsetPagination()
        paginator.default_limit = 20
        result_page = paginator.paginate_queryset(orgs, request)
        serializer = OrganizationSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def create_user(self, organization: Organization, email: str) -> None:
        """Creates a maintainer user for the organization."""
        User.objects.create(email=email, organization=organization, role="maintainer")

    @swagger_auto_schema(
        request_body=OrganizationSerializer,
        responses={201: "Success", 400: "Bad Request"},
    )
    @transaction.atomic
    def post(self, request: Request) -> Response:
        """Creates an organization."""

        email = request.user.email
        logger.info("Creating a new organization")
        serializer = OrganizationSerializer(data=request.data)
        print(request.data, "serialierorg")

        if not serializer.is_valid():
            logger.warning("Invalid organization data: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        organization = serializer.save()
        org_obj = Organization.objects.get(id=organization.id)
        self.create_user(org_obj, email)
        logger.info("Organization created with ID: %s", organization.id)
        return Response({"id": organization.id}, status=status.HTTP_201_CREATED)


class OrganizationDetailView(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(responses={200: "Success"})
    def get(self, request: Request, org_slug: str) -> Response:
        """Get organization by uuid"""
        logger.info("Fetching organization with slug: %s", org_slug)

        org = Organization.objects.get(slug=org_slug)
        serializer = OrganizationSerializer(org)
        return Response(serializer.data)

    @swagger_auto_schema(
        request_body=OrganizationSerializer,
        responses={201: "Success", 400: "Bad Request", 404: "Not Found"},
    )
    def patch(self, request: Request, org_slug: str) -> Response:
        """Updates an organization, given the uuid."""
        organization = get_object_or_404(Organization, slug=org_slug)
        serializer = OrganizationSerializer(
            organization, data=request.data, partial=True
        )
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer.save()
        return Response(status=status.HTTP_200_OK)


class OrganizationMaintainersView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        BelongsToOrganization,
        IsMaintainerOrAdmin,
    ]

    @swagger_auto_schema(responses={200: "Success"})
    def get(self, request: Request, org_slug: str) -> Response:
        """Get all maintainers for an organization"""
        organization = get_object_or_404(Organization, slug=org_slug)
        maintainers = User.objects.filter(organization=organization)
        serializer = MaintainerSerializer(maintainers, many=True)
        return Response(serializer.data)

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
        BelongsToOrganization,
        IsMaintainerOrAdmin,
    ]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
        ),
        responses={
            200: "Success",
            400: "Bad Request",
            403: "Forbidden",
            404: "Not Found",
        },
    )
    def delete(self, request: Request, org_slug: str, maintainer_id: str) -> Response:
        """Remove a maintainer from an organization"""

        if not maintainer_id:
            return Response(
                {"error": "Maintainer id is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        if maintainer_id == request.user.id:
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
                {
                    "error": "User is not a maintainer of this organization"
                },
                status=status.HTTP_404_NOT_FOUND,
            )
