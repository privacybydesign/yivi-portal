from django import conf

from schememanager.models.organization import Organization


def organizations(request):
    accessible = Organization.objects.filter(
        admins__email=request.session.get("yivi_email", None)
    ).order_by("legal_name")

    return {"accessible_organizations": accessible}


def settings(request):
    return {"settings": conf.settings}
