from .base import *  # noqa: F405, F403
import os

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

DEBUG = False

# Cross-Origin Resource Sharing (CORS)
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",")
CORS_ALLOW_CREDENTIALS = True

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("POSTGRES_DB"),
        "USER": os.environ.get("POSTGRES_USER"),
        "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST"),
        "PORT": os.environ.get("POSTGRES_PORT"),
    }
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATICFILES_STORAGE = (
    "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"  # Storage provider
)

# Static and Media Paths specific to production docker image
STATIC_URL = os.environ.get("STATIC_URL")
MEDIA_URL = os.environ.get("MEDIA_URL")
STATIC_ROOT = os.environ.get("STATIC_ROOT")
MEDIA_ROOT = os.environ.get("MEDIA_ROOT")

EMAIL_DISCLOSURE = [[["pbdf.sidn-pbdf.email.email"]]]
