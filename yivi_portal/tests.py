import importlib
import os
from unittest.mock import patch

from django.test import SimpleTestCase

# The bare minimum the production settings module needs to import at all.
PRODUCTION_ENV = {
    "DJANGO_SECRET_KEY": "test-secret-key",
    "JWT_SIGNING_KEY": "test-signing-key",
    "STATIC_URL": "/static/",
    "MEDIA_URL": "/media/",
    "STATIC_ROOT": "/tmp/static",
    "MEDIA_ROOT": "/tmp/media",
}


class ProductionSettingsTest(SimpleTestCase):
    """django-silk is a development tool and must stay out of production.

    Silk records request and response bodies, including Authorization headers,
    and serves its dashboard without access control of its own, so loading it
    in a deployed environment would expose credentials. It is added in
    settings/development.py; these tests pin that it does not reach
    settings/production.py, by either route: being listed in settings/base.py,
    or settings/development.py mutating a list base.py shares with it.
    """

    def _load_production_settings(self):
        with patch.dict(os.environ, PRODUCTION_ENV):
            module = importlib.import_module("yivi_portal.settings.production")
            # A previous import is cached, and settings/development.py has been
            # imported by the time the suite runs, so re-execute the module.
            return importlib.reload(module)

    def test_silk_app_not_installed_in_production(self):
        production = self._load_production_settings()
        self.assertNotIn("silk", production.INSTALLED_APPS)

    def test_silk_middleware_not_installed_in_production(self):
        production = self._load_production_settings()
        self.assertNotIn(
            "silk.middleware.SilkyMiddleware",
            production.MIDDLEWARE,
        )
