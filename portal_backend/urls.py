from django.urls import path
from portal_backend.views.trust_model import (
    TrustModelListView,
    TrustModelDetailView,
    TrustModelEnvironments,
    TrustModelEnvironment,
)
from portal_backend.views.organization import (
    OrganizationListView,
    OrganizationCreateView,
    OrganizationUpdateView,
    OrganizationDetailView,
    OrganizationMaintainersView,
    OrganizationMaintainerView,
)
from portal_backend.views.attestation_provider import (
    AttestationProviderListView,
    CredentialListView,
)
from portal_backend.views.relying_party import (
    RelyingPartyHostnameStatusView,
    RelyingPartyListView,
    RelyingPartyCreateView,
    RelyingPartyUpdateView,
    RelyingPartyRetrieveView,
    RelyingPartyDeleteView,
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
        "v1/organizations/",
        OrganizationListView.as_view(),
        name="organization-list",
    ),
    path(
        "v1/organizations/create/",
        OrganizationCreateView.as_view(),  # TODO: update frontend to use this endpoint
        name="organization-create",
    ),
    path(
        "v1/organizations/<str:org_slug>/update/",  # TODO: update frontend to use this endpoint
        OrganizationUpdateView.as_view(),
        name="organization-update",
    ),
    path(
        "v1/organizations/<str:org_slug>/",
        OrganizationDetailView.as_view(),
        name="organization-detail",
    ),
    path(
        "v1/organizations/<str:org_slug>/maintainers/",
        OrganizationMaintainersView.as_view(),
        name="organization-maintainers",
    ),
    path(
        "v1/organizations/<str:org_slug>/maintainers/<str:maintainer_id>/",
        OrganizationMaintainerView.as_view(),
        name="organization-maintainers",
    ),
    # Relying Party
    path(
        "v1/yivi/organizations/<str:org_slug>/relying-party/",
        RelyingPartyListView.as_view(),
        name="rp-list",
    ),
    path(
        "v1/yivi/organizations/<str:org_slug>/relying-party/create/",
        RelyingPartyCreateView.as_view(),
        name="rp-create",
    ),
    path(
        "v1/yivi/organizations/<str:org_slug>/relying-party/<str:rp_slug>/",
        RelyingPartyUpdateView.as_view(),
        name="rp-update",
    ),
    path(
        "v1/yivi/organizations/<str:org_slug>/relying-party/<str:environment>/<str:rp_slug>/",
        RelyingPartyRetrieveView.as_view(),
        name="rp-detail",
    ),
    path(
        "v1/yivi/organizations/<str:org_slug>/relying-party/<str:environment>/<str:rp_slug>/delete/",
        RelyingPartyDeleteView.as_view(),
        name="rp-delete",
    ),
    path(
        "v1/yivi/organizations/<str:org_slug>/relying-party/<str:environment>/<str:rp_slug>/dns-verification/",
        RelyingPartyHostnameStatusView.as_view(),
        name="rp-hostname-status",
    ),
    path("v1/credentials/", CredentialListView.as_view(), name="credential-list"),
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
