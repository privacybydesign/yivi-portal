from rest_framework import serializers
from .models import (
    Organization,
    TrustModel,
    User,
    YiviTrustModelEnv,
    Status,
    RelyingPartyHostname,
    Condiscon,
    AttestationProvider,
    Credential,
    CredentialAttribute,
    CondisconAttribute,
    RelyingParty,
)
from typing import Optional


class OrganizationSerializer(serializers.ModelSerializer):
    trust_model = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            "id",
            "name_en",
            "name_nl",
            "slug",
            "registration_number",
            "contact_address",
            "is_verified",
            "verified_at",
            "trade_names",
            "logo",
            "created_at",
            "last_updated_at",
            "is_RP",
            "is_AP",
            "trust_model",
        ]
        read_only_fields = ["is_verified"]

    def get_trust_model(self, obj: Organization) -> Optional[str]:
        return obj.trust_model.name if obj.trust_model else None


class TrustModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrustModel
        fields = ["id", "name", "description", "eudi_compliant"]


class YiviTrustModelEnvSerializer(serializers.ModelSerializer):
    class Meta:
        model = YiviTrustModelEnv
        fields = "__all__"


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
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
        fields = "__all__"


class CondisconAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CondisconAttribute
        fields = "__all__"


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
