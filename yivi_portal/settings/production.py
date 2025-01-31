import sys

from .base import *  # noqa

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")

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

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

STATIC_URL = os.environ.get("DJANGO_STATIC_URL")
MEDIA_URL = os.environ.get("DJANGO_MEDIA_URL")

STATIC_ROOT = os.environ.get("DJANGO_STATIC_ROOT")
MEDIA_ROOT = os.environ.get("DJANGO_MEDIA_ROOT")

EMAIL_DISCLOSURE = [
    [
        [ "pbdf.sidn-pbdf.email.email" ]
    ]
]

KVK_DISCLOSURE = [
    [
        [
            "pbdf.signicat.kvkTradeRegister.kvkNumber",
            "pbdf.signicat.kvkTradeRegister.name",
            "pbdf.signicat.kvkTradeRegister.tradeNames",
            "pbdf.signicat.kvkTradeRegister.typeOwner",
            "pbdf.signicat.kvkTradeRegister.legalEntity",
            "pbdf.signicat.kvkTradeRegister.address",
            "pbdf.signicat.kvkTradeRegister.emailAddress",
            "pbdf.signicat.kvkTradeRegister.phone",
            "pbdf.signicat.kvkTradeRegister.registrationStart",
            "pbdf.signicat.kvkTradeRegister.dateDeregistration",
            "pbdf.signicat.kvkTradeRegister.registrationEnd",
            "pbdf.signicat.kvkTradeRegister.specialLegalSituation",
            "pbdf.signicat.kvkTradeRegister.restrictionInLegalAction",
            "pbdf.signicat.kvkTradeRegister.foreignLegalStatus",
            "pbdf.signicat.kvkTradeRegister.hasRestriction",
            "pbdf.signicat.kvkTradeRegister.isAuthorized",
            "pbdf.signicat.kvkTradeRegister.reason",
            "pbdf.signicat.kvkTradeRegister.referenceMoment",
        ]
    ],
    [
        [
            "pbdf.sidn-pbdf.email.email"
        ]
    ],
]