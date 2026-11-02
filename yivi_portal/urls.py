from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/logout/", RedirectView.as_view(url="/logout", query_string=True)),
    path("admin/", admin.site.urls),
    path("", include("portal_backend.urls")),
    path("", include("yivi_auth.urls")),
    # Serve media files separately
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# The silk profiling dashboard is only mounted where silk is installed, which is
# the development settings module.
if "silk" in settings.INSTALLED_APPS:
    urlpatterns += [path("silk/", include("silk.urls"))]
