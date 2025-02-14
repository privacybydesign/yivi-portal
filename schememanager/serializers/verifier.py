from rest_framework import serializers
from fqdn import FQDN
from schememanager.models.verifier import (
    Verifier,
    VerifierHostname,
    VerifierSessionRequest,
)

class VerifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Verifier
        fields = [
            "scheme",
            "slug",
            "organization",
            "name_en",
            "name_nl",
            "logo",
        ]

class VerifierHostnameSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerifierHostname
        fields = [
            "hostname",
        ]

    def clean_hostname(self):
        hostname = self.cleaned_data["hostname"]
        fqdn = FQDN(hostname)
        if not fqdn.is_valid or fqdn.labels_count < 2:
            raise forms.ValidationError("Invalid hostname")
        
class VerifierSessionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = VerifierSessionRequest
        fields = [
            "condiscon",
        ]
    def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields["condiscon"] = forms.CharField(
                widget=forms.Textarea
            )  # Override to not display empty value as "null"
            self.fields["condiscon"].widget.attrs["rows"] = 4
            self.fields["condiscon"].widget.attrs["cols"] = 80
            self.fields["condiscon"].widget.attrs["style"] = "font-family: monospace"
            self.fields["condiscon"].widget.attrs["placeholder"] = json.dumps(
                {
                    "@context": "https://irma.app/ld/request/disclosure/v2",
                    "disclose": settings.EMAIL_DISCLOSURE,
                }
            )
        
    def clean_condiscon(self):
        try:
            condiscon = json.loads(self.cleaned_data["condiscon"])
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid JSON")

        if (
            "@context" not in condiscon
            or "disclose" not in condiscon
            or condiscon["@context"]
            not in [
                "https://irma.app/ld/request/disclosure/v2",
                "https://irma.app/ld/request/signature/v2",
            ]
        ):
            raise forms.ValidationError("Invalid condiscon")

        # TODO: More validation can be done here
        return condiscon
