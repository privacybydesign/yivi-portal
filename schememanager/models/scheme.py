from django.db import models


class Scheme(models.Model):
    """A scheme that is registered in the system"""

    REQUESTOR = "requestor"
    ISSUER = "issuer"

    SCHEME_TYPES = (
        (REQUESTOR, "Requestor"),
        (ISSUER, "Issuer"),
    )

    id = models.SlugField(max_length=100, primary_key=True)
    scheme_type = models.CharField(max_length=10, choices=SCHEME_TYPES)
    production = models.BooleanField(default=False)
    url = models.URLField()

    name_nl = models.CharField(max_length=100, null=True, blank=True)
    name_en = models.CharField(max_length=100, null=True, blank=True)
    description_nl = models.TextField(null=True, blank=True)
    description_en = models.TextField(null=True, blank=True)
    timestamp_server = models.URLField(null=True, blank=True)
    keyshare_server = models.URLField(null=True, blank=True)
    keyshare_website = models.URLField(null=True, blank=True)
    keyshare_attribute = models.CharField(max_length=100, null=True, blank=True)
    contact_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.id
