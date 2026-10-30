from django.contrib.admin import apps as admin_apps


class PortalAdminConfig(admin_apps.AdminConfig):
    """Django admin, served by the site that also asks for a Yivi disclosure."""

    # yivi_portal is an installed app too; it keeps a plain AppConfig, and this
    # config is only used where INSTALLED_APPS names it.
    default = False
    default_site = "yivi_portal.admin_site.YiviAdminSite"
