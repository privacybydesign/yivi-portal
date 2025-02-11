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

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR.parent / "db.sqlite3",
    }
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

KVK_DISCLOSURE = [
    [
        [
            "irma-demo.kvk.official.kvkNumber",
            "irma-demo.kvk.official.name",
            "irma-demo.kvk.official.tradeNames",
            "irma-demo.kvk.official.typeOwner",
            "irma-demo.kvk.official.legalEntity",
            "irma-demo.kvk.official.officeAddress",
            "irma-demo.kvk.official.emailAddress",
            "irma-demo.kvk.official.officePhone",
            "irma-demo.kvk.official.registrationStart",
            "irma-demo.kvk.official.dateDeregistration",
            "irma-demo.kvk.official.registrationEnd",
            "irma-demo.kvk.official.specialLegalSituation",
            "irma-demo.kvk.official.restrictionInLegalAction",
            "irma-demo.kvk.official.foreignLegalStatus",
            "irma-demo.kvk.official.hasRestriction",
            "irma-demo.kvk.official.isAuthorized",
            "irma-demo.kvk.official.reason",
            "irma-demo.kvk.official.referenceMoment",
        ]
    ],
    [
        [
            "irma-demo.sidn-pbdf.email.email"
        ]
    ],
]