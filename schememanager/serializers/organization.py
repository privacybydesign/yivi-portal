from rest_framework import serializers
from schememanager.models.organization import (
    Organization,
    OrganizationAdmin,
)

class OrganizationLegalSerializer(serializers.ModelSerializer):
    legal_trade_names = serializers.CharField()

    class Meta:
        model = Organization
        fields = [
            "legal_registration_number",
            "legal_name",
            "legal_trade_names",
            "legal_email",
            "legal_address",
            "legal_reference_moment",
        ]

class OrganizationBillingSerializer(serializers.ModelSerializer):
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

class OrganizationAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationAdmin
        fields = [
            "email",
        ]
