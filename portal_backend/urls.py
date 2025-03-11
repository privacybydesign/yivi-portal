from django.urls import path
from portal_backend.views.trust_model import *
from portal_backend.views.organization import *
from portal_backend.views.attestation_provider import *
from portal_backend.views.relying_party import *
from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


app_name = "portal_backend"

schema_view = get_schema_view(
   openapi.Info(
      title="Yivi API",
      default_version='v1',
      description="Yivi API"
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("v1/organizations", OrganizationListAPIView.as_view(), name="organizations"),
    path("v1/organizations/<uuid:pk>", OrganizationDetailAPIView.as_view(), name="organization-detail"),
    path("v1/organizations/<uuid:pk>/maintainers", OrganizationMaintainersAPIView.as_view(), name="organization-maintainers"),
    path("v1/trust-models", TrustModelListAPIView.as_view(), name="trust-models"),
    path("v1/trust-models/<str:name>/", TrustModelDetailAPIView.as_view(), name="trust-model-detail-with-environment"),
    path("v1/trust-models/<str:name>/environments", TrustModelEnvironments.as_view(), name="trust-model-environments"),
    path("v1/trust-models/<str:name>/environments/<str:environment>", TrustModelEnvironment.as_view(), name="trust-model-environment"),
    path("v1/trust-models/<str:name>/environments/<str:environment>/attestation-providers/", AttestationProviderListAPIView.as_view(), name="trust-model-list-with-environment"),
    path("v1/trust-models/<str:name>/environments/<str:environment>/relying-parties/", RelyingPartyListAPIView.as_view(), name="trust-model-list-with-environment"),
    path("v1/organizations/<uuid:pk>/relying-party", RelyingPartyRegisterAPIView.as_view(), name="register-relying-party"),
    path("v1/relying-party/<str:slug>/hostname/status/", RelyingPartyHostnameStatusAPIView.as_view(), name="hostname-status"),
   path("v1/relying-party/<str:slug>/status/", RelyingPartyRegistrationStatusAPIView.as_view(), name="RP-Registration-Status"),
   ]
