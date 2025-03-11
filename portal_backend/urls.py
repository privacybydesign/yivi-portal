from django.urls import path
from portal_backend.views.trust_model import (
    TrustModelListAPIView,
    TrustModelDetailAPIView,
    TrustModelEnvironments,
    TrustModelEnvironment,
)
from portal_backend.views.organization import (
    OrganizationListAPIView,
    OrganizationDetailAPIView,
    OrganizationMaintainersAPIView,
)
from portal_backend.views.attestation_provider import (
    AttestationProviderListAPIView,
)
from portal_backend.views.relying_party import (
    RelyingPartyRegisterAPIView,
    RelyingPartyListAPIView,
    RelyingPartyHostnameStatusAPIView,
    RelyingPartyRegistrationStatusAPIView,
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
        "v1/organizations/", OrganizationListAPIView.as_view(), name="organization-list"
    ),
    path(
        "v1/organizations/<uuid:pk>/",
        OrganizationDetailAPIView.as_view(),
        name="organization-detail",
    ),
    path(
        "v1/organizations/<uuid:pk>/maintainers/",
        OrganizationMaintainersAPIView.as_view(),
        name="organization-maintainers",
    ),
    # Organization Registration as AP or RP
    path(
        "v1/organizations/<uuid:pk>/register-rp/",
        RelyingPartyRegisterAPIView.as_view(),
        name="organization-register-rp",
    ),
    # Trust Models
    path("v1/trust-models/", TrustModelListAPIView.as_view(), name="trust-model-list"),
    path(
        "v1/trust-models/<str:name>/",
        TrustModelDetailAPIView.as_view(),
        name="trust-model-detail",
    ),
    # Trust Model Environments
    path(
        "v1/trust-models/<str:name>/environments/",
        TrustModelEnvironments.as_view(),
        name="trust-model-environment-list",
    ),
    path(
        "v1/trust-models/<str:name>/environments/<str:environment>/",
        TrustModelEnvironment.as_view(),
        name="trust-model-environment-detail",
    ),
    # Public Listings inside a Trust Model Environment
    path(
        "v1/trust-models/<str:name>/environments/<str:environment>/organizations/",
        OrganizationListAPIView.as_view(),
        name="trust-model-organization-list",
    ),
    path(
        "v1/trust-models/<str:name>/environments/<str:environment>/attestation-providers/",
        AttestationProviderListAPIView.as_view(),
        name="trust-model-ap-list",
    ),
    path(
        "v1/trust-models/<str:name>/environments/<str:environment>/relying-parties/",
        RelyingPartyListAPIView.as_view(),
        name="trust-model-rp-list",
    ),
    # Relying Party Statuses
    path(
        "v1/relying-parties/<str:slug>/hostname-status/",
        RelyingPartyHostnameStatusAPIView.as_view(),
        name="rp-hostname-status",
    ),
    path(
        "v1/relying-parties/<str:slug>/registration-status/",
        RelyingPartyRegistrationStatusAPIView.as_view(),
        name="rp-registration-status",
    ),
]
