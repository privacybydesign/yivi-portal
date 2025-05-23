from django.contrib import admin
from portal_backend.models.models import (
    Organization,
    TrustModel,
    YiviTrustModelEnv,
    RelyingPartyHostname,
    Condiscon,
    AttestationProvider,
    Credential,
    CredentialAttribute,
    CondisconAttribute,
    RelyingParty,
    User,
)


@admin.register(CredentialAttribute)
class CredentialAttributeAdmin(admin.ModelAdmin):
    list_display = (
        "name_en",
        "description_en",
        "get_credential",
        "get_credential_full_path",
    )
    search_fields = ("name_en", "description_en", "credential__name_en")

    @admin.display(description="Credential")
    def get_credential(self, obj):
        return obj.credential.name_en

    @admin.display(description="Identifier")
    def get_credential_full_path(self, obj):
        return obj.credential.full_path + "." + obj.credential_attribute_id


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name_en", "registration_number", "created_at", "last_updated_at")
    search_fields = ("name_en", "name_nl", "registration_number")
    list_filter = ("created_at", "last_updated_at")
    prepopulated_fields = {"slug": ("name_en",)}
    readonly_fields = ("created_at", "last_updated_at")


@admin.register(TrustModel)
class TrustModelAdmin(admin.ModelAdmin):
    list_display = ("name", "eudi_compliant")
    search_fields = ("name",)
    list_filter = ("eudi_compliant",)


@admin.register(YiviTrustModelEnv)
class YiviTrustModelEnvAdmin(admin.ModelAdmin):
    list_display = ("trust_model", "environment", "timestamp_server", "keyshare_server")
    search_fields = ("trust_model__name", "environment", "timestamp_server")
    list_filter = ("environment",)


@admin.register(RelyingPartyHostname)
class RelyingPartyHostnameAdmin(admin.ModelAdmin):
    list_display = ("hostname", "dns_challenge_verified", "manually_verified")
    list_filter = ("dns_challenge_verified", "manually_verified")
    search_fields = ("hostname",)


@admin.register(Condiscon)
class CondisconAdmin(admin.ModelAdmin):
    list_display = ("context_description_en", "context_description_nl")
    search_fields = ("context_description_en", "context_description_nl")


@admin.register(AttestationProvider)
class AttestationProviderAdmin(admin.ModelAdmin):
    list_display = (
        "organization",
        "yivi_tme",
        "version",
        "ready",
        "reviewed_accepted",
        "published_at",
    )
    search_fields = ("organization__name_en", "version")
    list_filter = ("yivi_tme", "ready", "reviewed_accepted", "published_at")
    readonly_fields = ("created_at", "last_updated_at")


@admin.register(Credential)
class CredentialAdmin(admin.ModelAdmin):
    list_display = (
        "name_en",
        "description_en",
        "attestation_provider",
        "get_full_path",
    )
    search_fields = ["name_en"]

    def get_full_path(self, obj):
        return obj.full_path

    get_full_path.short_description = "Credential Identifier"


class CondisconAttributeInline(admin.TabularInline):
    model = CondisconAttribute
    extra = 1
    autocomplete_fields = ["credential_attribute"]


@admin.register(CondisconAttribute)
class CondisconAttributeAdmin(admin.ModelAdmin):
    list_display = ("credential_attribute", "condiscon", "reason_en", "reason_nl")
    search_fields = ("credential_attribute__name_en", "reason_en", "reason_nl")
    list_filter = ("condiscon",)


@admin.register(RelyingParty)
class RelyingPartyAdmin(admin.ModelAdmin):
    list_display = (
        "organization",
        "rp_slug",
        "yivi_tme",
        "ready",
        "reviewed_accepted",
        "published_at",
        "created_at",
        "last_updated_at",
        "get_hostnames",
    )
    search_fields = (
        "organization__name_en",
        "organization__name_nl",
        "rp_slug",
        "hostnames__hostname",
    )
    list_filter = ("yivi_tme", "ready", "reviewed_accepted", "published_at")
    readonly_fields = ("created_at", "last_updated_at")

    def get_hostnames(self, obj):
        return ", ".join(obj.hostnames.values_list("hostname", flat=True))

    get_hostnames.short_description = "Hostnames"


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "get_organizations", "role")

    @admin.display(description="Organizations")
    def get_organizations(self, obj):
        return ", ".join([org.slug for org in obj.organizations.all()])
