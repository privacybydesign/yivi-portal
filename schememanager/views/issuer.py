from django.views.generic import TemplateView


class IssuerPortalView(TemplateView):
    template_name = "issuer/issuer.html"
