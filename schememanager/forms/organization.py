from django.forms import ModelForm

from schememanager.models.organization import Organization, OrganizationAdmin


class OrganizationLegalForm(ModelForm):
    class Meta:
        model = Organization
        fields = [
            "legal_registration_number",
            "legal_name",
            "legal_trade_names",  # TODO: display this in a better way
            "legal_email",
            "legal_address",
            "legal_reference_moment",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            # Disable all fields because they are not editable
            self.fields[field].disabled = True
        self.fields["legal_trade_names"].widget.attrs["rows"] = 2
        self.fields["legal_trade_names"].widget.attrs["cols"] = 80
        self.fields["legal_address"].widget.attrs["rows"] = 4
        self.fields["legal_address"].widget.attrs["cols"] = 80


class OrganizationBillingForm(ModelForm):
    class Meta:
        model = Organization
        fields = [
            "billing_email",
            "billing_address",
            "billing_postal_code",
            "billing_city",
            "billing_country",
        ]
        # TODO: display this in a better way with more input validation (e.g. postal code, country. Maybe use a
        #  widget for the country field)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["billing_address"].widget.attrs["rows"] = 2
        self.fields["billing_address"].widget.attrs["cols"] = 80


class OrganizationAdminForm(ModelForm):
    class Meta:
        model = OrganizationAdmin
        fields = [
            "email",
        ]
