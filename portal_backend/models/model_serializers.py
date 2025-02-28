from rest_framework import serializers
from .models import *

class OrganizationSerializer(serializers.ModelSerializer):
    is_RP = serializers.SerializerMethodField()
    is_AP = serializers.SerializerMethodField()
    trust_model = serializers.SerializerMethodField()
    class Meta:
        model = Organization
        fields = [
            'id', 'name_en', 'name_nl', 'slug',
            'registration_number', 'address', 'is_verified',
            'verified_at', 'trade_names', 'logo', 'created_at', 'last_updated_at',
            'is_RP', 'is_AP', 'trust_model']
        read_only_fields = ['is_verified']

    def get_is_RP(self, obj):
        return RelyingParty.objects.filter(
            organization=obj,
            status__reviewed_accepted=True
        ).exists()
    
    def get_is_AP(self, obj):
        return AttestationProvider.objects.filter(
            organization=obj,
            status__reviewed_accepted=True
        ).exists()
    
    def get_trust_model(self, obj):
        # check for trust model in AP
        ap = AttestationProvider.objects.filter(organization=obj).first()
        if ap and ap.yivi_tme and ap.yivi_tme.trust_model:
            return ap.yivi_tme.trust_model.name
        
        # check for trust model in RP
        rp = RelyingParty.objects.filter(organization=obj).first()
        if rp and rp.yivi_tme and rp.yivi_tme.trust_model:
            return rp.yivi_tme.trust_model.name
        
        return None

class TrustModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrustModel
        fields = ['id', 'name', 'description', 'eudi_compliant']

class YiviTrustModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = YiviTrustModelEnv
        fields = '__all__'

class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = '__all__'

class RelyingPartyHostnameSerializer(serializers.ModelSerializer):
    class Meta:
        model = RelyingPartyHostname
        fields = '__all__'

class CondisconSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condiscon
        fields = '__all__'

class AttestationProviderSerializer(serializers.ModelSerializer):
    yivi_tme = serializers.CharField(source='yivi_tme.environment' , read_only=True)
    organization = serializers.CharField(source='organization.name_en', read_only=True)
    status = serializers.BooleanField(source='status.reviewed_accepted', read_only=True)
    class Meta:
        model = AttestationProvider
        fields = '__all__'

class CredentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credential
        fields = '__all__'

class CredentialAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CredentialAttribute
        fields = '__all__'

class CondisconAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CondisconAttribute
        fields = '__all__'

class RelyingPartySerializer(serializers.ModelSerializer):
    yivi_tme = serializers.CharField(source='yivi_tme.environment' , read_only=True)
    organization = serializers.CharField(source='organization.name_en', read_only=True)
    status = serializers.BooleanField(source='status.reviewed_accepted', read_only=True)
    hostname = serializers.CharField(source='hostname.hostname', read_only=True)
    condiscon = serializers.JSONField(source='condiscon.condiscon', read_only=True)
    class Meta:
        model = RelyingParty
        fields = '__all__'