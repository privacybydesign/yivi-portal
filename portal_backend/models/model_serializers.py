from rest_framework import serializers
from .models import (
    Organization,
    TrustModel,
    User,
    YiviTrustModelEnv,
    RelyingPartyHostname,
    Condiscon,
    AttestationProvider,
    Credential,
    CredentialAttribute,
    CondisconAttribute,
    RelyingParty,
)
from django_countries.serializers import CountryFieldMixin  # type: ignore


class TrustModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrustModel
        fields = ["id", "name", "description", "eudi_compliant"]


class OrganizationSerializer(CountryFieldMixin, serializers.ModelSerializer):
    trust_models = TrustModelSerializer(many=True, read_only=True)

    is_RP = serializers.BooleanField(source="is_rp", read_only=True)
    is_AP = serializers.BooleanField(source="is_ap", read_only=True)
    logo = serializers.ImageField(required=False)

    class Meta:
        model = Organization
        fields = [
            "id",
            "name_en",
            "name_nl",
            "slug",
            "is_verified",
            "verified_at",
            "logo",
            "created_at",
            "last_updated_at",
            "is_RP",
            "is_AP",
            "trust_models",
            "country",
            "house_number",
            "street",
            "postal_code",
            "city",
        ]
        read_only_fields = ["is_verified"]


class YiviTrustModelEnvSerializer(serializers.ModelSerializer):
    class Meta:
        model = YiviTrustModelEnv
        fields = "__all__"


class RelyingPartyHostnameSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelyingPartyHostname
        fields = "__all__"


class CondisconSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condiscon
        fields = "__all__"


class AttestationProviderSerializer(serializers.ModelSerializer):
    yivi_tme = serializers.CharField(source="yivi_tme.environment", read_only=True)
    organization = serializers.CharField(source="organization.name_en", read_only=True)
    status = serializers.BooleanField(source="status.reviewed_accepted", read_only=True)
    organization_logo = serializers.ImageField(
        source="organization.logo", read_only=True
    )

    class Meta:
        model = AttestationProvider
        fields = [
            "id",
            "ap_slug",
            "organization",
            "yivi_tme",
            "contact_email",
            "contact_address",
            "credentials",
            "full_path",
            "status",
            "organization_logo",
        ]


class CredentialAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CredentialAttribute
        fields = [
            "id",
            "credential_attribute_id",
            "name_en",
            "name_nl",
            "description_en",
            "description_nl",
            "full_path",
        ]


class CredentialListSerializer(serializers.ModelSerializer):
    attributes = CredentialAttributeSerializer(many=True, read_only=True)
    org_slug = serializers.CharField(
        source="attestation_provider.organization.slug", read_only=True
    )
    org_name = serializers.CharField(
        source="attestation_provider.organization.name_en", read_only=True
    )
    environment = serializers.CharField(
        source="attestation_provider.yivi_tme.environment", read_only=True
    )
    ap_slug = serializers.CharField(
        source="attestation_provider.ap_slug", read_only=True
    )

    class Meta:
        model = Credential
        fields = [
            "id",
            "name_en",
            "name_nl",
            "org_slug",
            "org_name",
            "ap_slug",
            "environment",
            "credential_id",
            "attributes",
            "description_en",
            "description_nl",
            "full_path",
            "issue_url",
            "deprecated_since",
        ]


class CondisconAttributeSerializer(serializers.ModelSerializer):
    credential_attribute = serializers.CharField(
        source="credential_attribute.name_en", read_only=True
    )

    class Meta:
        model = CondisconAttribute
        fields = ["reason_en", "credential_attribute"]


class RelyingPartySerializer(serializers.ModelSerializer):
    yivi_tme = serializers.CharField(source="yivi_tme.environment", read_only=True)
    organization = serializers.CharField(source="organization.name_en", read_only=True)
    status = serializers.CharField(source="status.rp_status", read_only=True)

    class Meta:
        model = RelyingParty
        fields = "__all__"


class MaintainerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"
