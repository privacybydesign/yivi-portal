from schememanager.views.organization import SingleOrganizationPortalView


class IssuerPortalView(SingleOrganizationPortalView):
    template_name = "issuer/issuer.html"

    def dispatch(self, request, *args, **kwargs):
        raise NotImplementedError()
