from typing import Optional
from django.db.models import Exists, OuterRef, Q, QuerySet
from portal_backend.models.models import (
    AttestationProvider,
    Organization,
    RelyingParty,
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

    # If both select_aps and select_rps are False, return an empty list
    if select_aps is False and select_rps is False:
        return Organization.objects.none()

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
        orgs = orgs.filter(
            Q(name_en__icontains=search_query) | Q(name_nl__icontains=search_query)
        )

    if trust_model:
        orgs = orgs.filter(trust_models__name=trust_model)

    return orgs
