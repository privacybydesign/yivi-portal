from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path(
        "admin/login/",
        RedirectView.as_view(url="/login/?next=/admin/", query_string=True),
    ),
    path("admin/logout/", RedirectView.as_view(url="/logout", query_string=True)),
    path("admin/", admin.site.urls),
    path("", include("schememanager.urls")),
    path("", include("yivi_auth.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
