from typing import Optional
from django.db.models import Q, QuerySet
from portal_backend.models.models import (
    Organization,
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


def filter_organizations(
    request: Request,
) -> QuerySet:
    """Filter organizations based on query parameters"""

    search_query: Optional[str] = request.query_params.get("search")
    trust_model: Optional[str] = request.query_params.get("trust_model")
    select_aps: Optional[bool] = to_nullable_bool(request.query_params.get("ap"))
    select_rps: Optional[bool] = to_nullable_bool(request.query_params.get("rp"))

    filtered_orgs = Organization.objects.with_role_annotations().filter(
        Q(is_ap=True) | Q(is_rp=True)
    )

    if select_aps:
        filtered_orgs = filtered_orgs.filter(is_ap=True)
    if select_rps:
        filtered_orgs = filtered_orgs.filter(is_rp=True)

    if search_query:
        filtered_orgs = filtered_orgs.filter(
            Q(name_en__icontains=search_query) | Q(name_nl__icontains=search_query)
        )

    if trust_model:
        filtered_orgs = filtered_orgs.filter(trust_models__name=trust_model)

    return filtered_orgs.prefetch_related(
        "trust_models",
    )
