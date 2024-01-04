from schememanager.models.organization import Organization


def organizations(request):
    accessible = Organization.objects.filter(
        admins__email=request.session.get("yivi_email", None)
    )

    try:
        organization = Organization.objects.get(
            slug=request.resolver_match.kwargs.get("org_slug", None)
        )
    except Organization.DoesNotExist:
        organization = None

    return {"accessible_organizations": accessible, "organization": organization}
