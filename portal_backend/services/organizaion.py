from typing import Optional
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import Exists, OuterRef, Q, QuerySet
from portal_backend.models.model_serializers import OrganizationSerializer
from portal_backend.models.models import (
    AttestationProvider,
    Organization,
    RelyingParty,
    User,
)
from rest_framework.request import Request


def to_nullable_bool(value: Optional[str]) -> Optional[bool]:
    if value is None:
        return None
    value = value.lower()
    if value == "true":
        return True
    if value == "false":
        return False
    return None


def create_user(organization: Organization, email: str) -> None:
    """Creates a maintainer user for the organization."""
    User.objects.create(email=email, organization=organization, role="maintainer")


def filter_organizations(
    request: Request,
    search_query: Optional[str] = None,
    trust_model: Optional[str] = None,
    select_aps: Optional[bool] = None,
    select_rps: Optional[bool] = None,
) -> QuerySet:
    """Filter organizations based on query parameters"""

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
    # TODO: org that is not rp and not ap should still show up in the list
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
            name_nl__icontains=search_query
        )
    if trust_model:
        orgs = Organization.objects.filter(trust_models__name=trust_model)
    return orgs
