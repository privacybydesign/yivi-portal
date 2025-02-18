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
class KvkEntrySerializer(serializers.Serializer):
    kvk_number = serializers.CharField(max_length=20)
    name = serializers.CharField(max_length=200)
    trade_names = serializers.CharField(max_length=200)
    type_owner = serializers.CharField(max_length=100)
    legal_entity = serializers.CharField(max_length=100)
    address = serializers.CharField(max_length=300)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=20)
    registration_start = serializers.CharField(max_length=20)
    date_deregistration = serializers.CharField(max_length=20, required=False, allow_blank=True)
    registration_end = serializers.CharField(max_length=20, required=False, allow_blank=True)
    special_legal_situation = serializers.CharField(max_length=200, required=False, allow_blank=True)
    restriction_in_legal_action = serializers.CharField(max_length=200, required=False, allow_blank=True)
    foreign_legal_status = serializers.CharField(max_length=200, required=False, allow_blank=True)
    has_restriction = serializers.CharField(max_length=50, required=False, allow_blank=True)
    is_authorized = serializers.CharField(max_length=50, required=False, allow_blank=True)
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)
    reference_moment = serializers.CharField(max_length=50)

class RegistrationSerializer(serializers.Serializer):
    kvk_data = KvkEntrySerializer()
    yivi_email = serializers.EmailField()