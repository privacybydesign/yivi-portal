from .base import *  # noqa

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-!ar%l1@3bkc52!3l(a^$x9j46p#7wlxm^2$l$rtp8d1m-=dvf)"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

ALLOWED_HOSTS = ["*", "localhost", "127.0.0.1"]
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR.parent / "db.sqlite3",
    }
}

SWAGGER_SETTINGS = {
    "LOGIN_URL": None,  # Disable Django login button
    "USE_SESSION_AUTH": False,  # Disable session authentication
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Enter the token as: Bearer <token>"
        }
    },
    "DEFAULT_SECURITY": [
        {"Bearer": []}  # Apply Bearer auth globally
    ],
    "PERSIST_AUTH": True,  # Keep token saved in Swagger UI
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
MEDIA_URL = "assets/"

STATIC_ROOT = BASE_DIR / "static"
MEDIA_ROOT = BASE_DIR / "assets"

EMAIL_DISCLOSURE = [
    [
        [ "irma-demo.sidn-pbdf.email.email" ]
    ]
]

