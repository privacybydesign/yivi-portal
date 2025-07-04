from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path(
        "yivi-admin/logout/",
        RedirectView.as_view(url="/logout", query_string=True),
    ),
    path("yivi-admin/", admin.site.urls),
    path("", include("portal_backend.urls")),
    path("", include("yivi_auth.urls")),
    # Serve media files separately
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
