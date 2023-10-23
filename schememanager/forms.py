from django import forms
from django.forms import ModelForm

from schememanager.models import (
    Organization,
    OrganizationAdmin,
    Verifier,
    VerifierHostname,
    VerifierSessionRequest,
)


class OrganizationForm(ModelForm):
    class Meta:
        model = Organization
        fields = [
            "name",
            "kvk_number",
            "kvk_registration_start",
            "kvk_registration_end",
            "kvk_email",
            "billing_email",
            "billing_address",
            "billing_postal_code",
            "billing_city",
            "billing_country",
        ]


class OrganizationAdminForm(ModelForm):
    class Meta:
        model = OrganizationAdmin
        fields = [
            "email",
        ]


class VerifierForm(ModelForm):
    class Meta:
        model = Verifier
        fields = [
            "name_en",
            "name_nl",
            "description_en",
            "description_nl",
            "logo",
        ]


class VerifierHostnameForm(ModelForm):
    class Meta:
        model = VerifierHostname
        fields = [
            "hostname",
        ]


class VerifierSessionRequestAddForm(ModelForm):
    class Meta:
        model = VerifierSessionRequest
        fields = [
            "condiscon",
        ]
