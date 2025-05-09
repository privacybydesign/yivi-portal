from django.apps import AppConfig


class PortalBackendConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "portal_backend"

    def ready(self):
        import portal_backend.signals  # noqa: F401
