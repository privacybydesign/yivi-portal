from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.views.static import serve
from django.urls import re_path

from django.shortcuts import render

def nextjs_catchall(request, path=""):
    """Serve Next.js index.html for all unknown routes (client-side routing)."""
    print('tesstttttt', path)
    return render(request, "index.html")

urlpatterns = [
    path("admin/logout/", RedirectView.as_view(url="/logout", query_string=True)),
    path("admin/", admin.site.urls),
    path("", include("portal_backend.urls")),
    path("", include("yivi_auth.urls")),
    path("", nextjs_catchall, name="nextjs_app"),
    # Serve static files from root `/` (except for `/media/`)
    # re_path(r"^(?!media/)(?P<path>.*)$", serve, {"document_root": settings.STATICFILES_DIRS[0]}),
    # Catch all unknown frontend routes and serve index.html
    # Serve static files from root `/` (except for `/media/`)
    re_path(r"^(?!media/)(?P<path>.*)$", serve, {"document_root": settings.STATICFILES_DIRS[0]}),
]

# Serve media files separately
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)