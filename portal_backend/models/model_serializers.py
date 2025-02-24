from rest_framework import serializers
from .models import *

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'
        read_only_fields = ('is_verified',)


class TrustModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrustModel
        fields = '__all__'

class YiviTrustModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = YiviTrustModelEnv
        fields = '__all__'

class ApplicationStatus(serializers.ModelSerializer):
    class Meta:
        model = ApplicationStatus
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
    class Meta:
        model = RelyingParty
        fields = '__all__'
