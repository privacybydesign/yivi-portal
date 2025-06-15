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

    search_query = request.query_params.get("search")
    trust_model = request.query_params.get("trust_model")
    select_aps = to_nullable_bool(request.query_params.get("ap"))
    select_rps = to_nullable_bool(request.query_params.get("rp"))

    qs = Organization.objects.all()

    if search_query:
        qs = qs.filter(
            Q(name_en__icontains=search_query) | Q(name_nl__icontains=search_query)
        )

    qs = qs.exclude(Q(name_en__icontains="demo") | Q(name_nl__icontains="demo"))

    if trust_model:
        qs = qs.filter(trust_models__name=trust_model)

    qs = qs.with_role_annotations()

    if select_aps is True and select_rps is True:
        qs = qs.filter(is_ap=True, is_rp=True)
    elif select_aps is True:
        qs = qs.filter(is_ap=True)
    elif select_rps is True:
        qs = qs.filter(is_rp=True)
    else:
        qs = qs.filter(Q(is_ap=True) | Q(is_rp=True))

    return qs.prefetch_related("trust_models").distinct().order_by("name_en")
