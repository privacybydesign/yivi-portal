from django.contrib import admin
from portal_backend.models.models import (
    Organization, TrustModel, YiviTrustModelEnv, ApplicationStatus,
    RelyingPartyHostname, Condiscon, AttestationProvider, Credential,
    CredentialAttribute, CondisconAttribute, RelyingParty, User
)

# Organization Admin
@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'registration_number', 'created_at', 'last_updated_at')
    search_fields = ('name_en', 'name_nl', 'registration_number')
    list_filter = ('created_at', 'last_updated_at')
    prepopulated_fields = {'slug': ('name_en',)}
    readonly_fields = ('created_at', 'last_updated_at')

# TrustModel Admin
@admin.register(TrustModel)
class TrustModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'eudi_compliant')
    search_fields = ('name',)
    list_filter = ('eudi_compliant',)

# YiviTrustModelEnv Admin
@admin.register(YiviTrustModelEnv)
class YiviTrustModelEnvAdmin(admin.ModelAdmin):
    list_display = ('trust_model', 'environment', 'timestamp_server', 'keyshare_server')
    search_fields = ('trust_model__name', 'environment', 'timestamp_server')
    list_filter = ('environment',)

# ApplicationStatus Admin
@admin.register(ApplicationStatus)
class ApplicationStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'ready', 'reviewed_accepted', 'published_at')
    list_filter = ('ready', 'reviewed_accepted', 'published_at')
    readonly_fields = ('created_at', 'last_updated_at')

# RelyingPartyHostname Admin
@admin.register(RelyingPartyHostname)
class RelyingPartyHostnameAdmin(admin.ModelAdmin):
    list_display = ('hostname', 'dns_challenge_verified', 'manually_verified')
    list_filter = ('dns_challenge_verified', 'manually_verified')
    search_fields = ('hostname',)

# Condiscon Admin
@admin.register(Condiscon)
class CondisconAdmin(admin.ModelAdmin):
    list_display = ('context_description_en', 'context_description_nl')
    search_fields = ('context_description_en', 'context_description_nl')

# AttestationProvider Admin
@admin.register(AttestationProvider)
class AttestationProviderAdmin(admin.ModelAdmin):
    list_display = ('organization', 'yivi_tme', 'status', 'version')
    search_fields = ('organization__name_en', 'version')
    list_filter = ('status',)

# Inline model for Credential Attributes
class CredentialAttributeInline(admin.TabularInline):
    model = CredentialAttribute
    extra = 1  
    
# Credential Admin
@admin.register(Credential)
class CredentialAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'attestation_provider', 'credential_tag')
    search_fields = ('name_en', 'credential_tag')
    inlines = [CredentialAttributeInline] 

# Relying Party Admin
@admin.register(RelyingParty)
class RelyingPartyAdmin(admin.ModelAdmin):
    list_display = ('organization', 'yivi_tme', 'hostname', 'condiscon')
    search_fields = ('organization__name_en', 'hostname__hostname')
    list_filter = ('yivi_tme',)

# User Admin
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('organization', 'role')
    search_fields = ('organization__name_en', 'role')
    list_filter = ('role',)
