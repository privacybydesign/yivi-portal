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
            "registration_number",
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

    class Meta:
        model = AttestationProvider
        fields = "__all__"


class CredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credential
        fields = "__all__"


class CredentialAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CredentialAttribute
        fields = ""


class CondisconAttributeSerializer(serializers.ModelSerializer):
    credential_attribute = serializers.CharField(
        source="credential_attribute.credential.", read_only=True
    )

    class Meta:
        model = CondisconAttribute
        fields = ["reason-en", "credential_attribute"]


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
