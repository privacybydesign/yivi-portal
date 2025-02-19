from django.urls import path

from schememanager.views.trust_model import *
from schememanager.views.organizations import *

from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


app_name = "schememanager"

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

    path("v1/trust-models", TrustModelRestView.as_view(), name="trust-models"),
    path("v1/organizations", OrganizationsRestView.as_view(), name="organizations"),
]
