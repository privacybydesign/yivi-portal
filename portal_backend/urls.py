from django.urls import path
from drf_yasg import openapi  # type: ignore
from drf_yasg.views import get_schema_view  # type: ignore
from rest_framework import permissions

from portal_backend.views.attestation_provider import (
    AttestationProviderCredentialsListView,
    AttestationProviderListView,
    AttestationProviderRetrieveView,
)
from portal_backend.views.credentials import (
    CredentialListView,
    CredentialsListViewWithDeprecated,
)
from portal_backend.views.organization import (
    OrganizationCreateView,
    OrganizationDetailView,
    OrganizationListView,
    OrganizationMaintainersView,
    OrganizationMaintainerView,
    OrganizationNameAndSlugView,
    OrganizationUpdateView,
)
from portal_backend.views.relying_party import (
    RelyingPartyCreateView,
    RelyingPartyDeleteView,
    RelyingPartyHostnameStatusView,
    RelyingPartyListView,
    RelyingPartyRetrieveView,
    RelyingPartyUpdateView,
)
from portal_backend.views.trust_model import (
    TrustModelDetailView,
    TrustModelListView,
    YiviTrustModelEnvListView,
)
from portal_backend.views.usage import (
    UsageServerKeysView,
    UsageServerKeyView,
    UsageSummaryView,
    usage_account,
    usage_directory,
    usage_new_account,
    usage_new_nonce,
    usage_reports,
)

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
        "v1/organizations/<str:org_slug>/maintainers/<uuid:maintainer_id>/",
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
    # Trust Models
    path("v1/trust-models/", TrustModelListView.as_view(), name="trust-model-list"),
    path(
        "v1/trust-models/<str:name>/",
        TrustModelDetailView.as_view(),
        name="trust-model-detail",
    ),
    # Trust Model Environments
    path(
        "v1/<str:trust_model_name>/environments/",
        YiviTrustModelEnvListView.as_view(),
        name="trust-model-environment-list",
    ),
    # Credentials
    path("v1/yivi/credentials/", CredentialListView.as_view(), name="credential-list"),
    path(
        "v1/yivi/all-credentials/",
        CredentialsListViewWithDeprecated.as_view(),
        name="credentials-list-with-deprecated",
    ),
    # Attestation Providers
    path(
        "v1/yivi/organizations/<str:org_slug>/attestation-provider/",
        AttestationProviderListView.as_view(),
        name="trust-model-ap-list",
    ),
    path(
        "v1/yivi/organizations/<str:org_slug>/attestation-provider/<str:environment>/<str:ap_slug>/",
        AttestationProviderRetrieveView.as_view(),
    ),
    path(
        "v1/yivi/organizations/<str:org_slug>/attestation-provider/<str:environment>/<str:ap_slug>/credentials/",
        AttestationProviderCredentialsListView.as_view(),
        name="ap-credentials-list",
    ),
    # Usage reporting by self-hosted Yivi servers (ACME-shaped, authenticated by JWS)
    path("usage/v1/directory", usage_directory, name="usage-directory"),
    path("usage/v1/new-nonce", usage_new_nonce, name="usage-new-nonce"),
    path("usage/v1/new-account", usage_new_account, name="usage-new-account"),
    path("usage/v1/accounts/<uuid:key_id>", usage_account, name="usage-account"),
    path(
        "usage/v1/accounts/<uuid:key_id>/reports",
        usage_reports,
        name="usage-reports",
    ),
    # Usage reporting keys and usage of an organization
    path(
        "v1/organizations/<str:org_slug>/usage-keys/",
        UsageServerKeysView.as_view(),
        name="usage-keys",
    ),
    path(
        "v1/organizations/<str:org_slug>/usage-keys/<uuid:key_id>/",
        UsageServerKeyView.as_view(),
        name="usage-key",
    ),
    path(
        "v1/organizations/<str:org_slug>/usage/",
        UsageSummaryView.as_view(),
        name="usage-summary",
    ),
    path(
        "v1/profile",
        OrganizationNameAndSlugView.as_view(),
        name="organization-name-and-slug",
    ),
]
