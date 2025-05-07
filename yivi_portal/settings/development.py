from .base import *  # noqa: F405, F403
import os


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-4@v3!$#)7&*0g1@5^2b6j8z3q9r+qk5x!_v#(d@f1h0w4g3m2",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Cross-Origin Resource Sharing (CORS)
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS").split(",")
CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS").split(",")
CORS_ALLOW_CREDENTIALS = True

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR.parent / "db.sqlite3",  # noqa: F405
    }
}

# Swagger Settings
# https://django-rest-swagger.readthedocs.io/en/latest/settings/
SWAGGER_SETTINGS = {
    "LOGIN_URL": None,  # Disable Django login button
    "USE_SESSION_AUTH": False,  # Disable session authentication
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter the token as: Bearer <token>",
        }
    },
    "DEFAULT_SECURITY": [{"Bearer": []}],  # Apply Bearer auth globally
    "PERSIST_AUTH": True,  # Keep token saved in Swagger UI
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATICFILES_DIRS = [BASE_DIR.parent / "portal_backend" / "static"]  # noqa: F405

STATIC_ROOT = BASE_DIR / "static"  # noqa: F405
MEDIA_ROOT = BASE_DIR / "assets"  # noqa: F405
STATIC_URL = "/static/"  # noqa: F405
MEDIA_URL = "/assets/"  # noqa: F405


EMAIL_DISCLOSURE = [[["irma-demo.sidn-pbdf.email.email"]]]
