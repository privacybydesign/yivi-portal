from django.urls import path
from portal_backend.views.trust_model import (
    TrustModelListView,
    TrustModelDetailView,
    TrustModelEnvironments,
    TrustModelEnvironment,
)
from portal_backend.views.organization import (
    OrganizationListView,
    OrganizationDetailView,
    OrganizationMaintainersView,
)
from portal_backend.views.attestation_provider import (
    AttestationProviderListView,
)
from portal_backend.views.relying_party import (
    RelyingPartyRegisterView,
    RelyingPartyDetailView,
    RelyingPartyHostnameStatusView,
    RelyingPartyUpdateView,
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view  # type: ignore
from drf_yasg import openapi  # type: ignore

app_name = "portal_backend"

schema_view = get_schema_view(
    openapi.Info(title="Yivi API", default_version="v1", description="Yivi API"),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Documentation Endpoints
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # Organizations
    path(
        "v1/yivi/organizations/",
        OrganizationListView.as_view(),
        name="organization-list",
    ),
    path(
        "v1/yivi/organizations/<str:org_slug>/",
        OrganizationDetailView.as_view(),
        name="organization-detail",
    ),
    path(
        "v1/yivi/organizations/<str:org_slug>/maintainers/",
        OrganizationMaintainersView.as_view(),
        name="organization-maintainers",
    ),
    # Relying Party
    path(
        "v1/yivi/organizations/<str:org_slug>/relying-party/",
        RelyingPartyRegisterView.as_view(),
        name="organization-register-rp",
    ),
    path(
        "v1/yivi/organizations/<str:org_slug>/relying-party/<str:environment>/<str:rp_slug>/",
        RelyingPartyDetailView.as_view(),
        name="organization-rp-list",
    ),
    path(
        "v1/yivi/organizations/<str:org_slug>/relying-party/<str:rp_slug>/",
        RelyingPartyUpdateView.as_view(),
        name="organization-rp-manage",
    ),
    path(
        "v1/yivi/organizations/<str:org_slug>/relying-party/<str:environment>/<str:rp_slug>/dns-verification/",
        RelyingPartyHostnameStatusView.as_view(),
        name="rp-hostname-status",
    ),
    # Trust Models
    path("v1/trust-models/", TrustModelListView.as_view(), name="trust-model-list"),
    path(
        "v1/trust-models/<str:name>/",
        TrustModelDetailView.as_view(),
        name="trust-model-detail",
    ),
    # Trust Model Environments
    path(
        "v1/<str:name>/environments/",
        TrustModelEnvironments.as_view(),
        name="trust-model-environment-list",
    ),
    path(
        "v1/<str:trustmodel_name>/<str:environment>/",
        TrustModelEnvironment.as_view(),
        name="trust-model-environment-detail",
    ),
    # Public Listings inside a Trust Model Environment
    path(
        "v1/<str:trustmodel_name>/<str:environment>/attestation-providers/",
        AttestationProviderListView.as_view(),
        name="trust-model-ap-list",
    ),
]
