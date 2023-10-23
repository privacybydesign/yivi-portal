from django.contrib import admin

from schememanager import models


class OrganizationAdminInline(admin.StackedInline):
    model = models.OrganizationAdmin
    extra = 0


@admin.register(models.Organization)
class OrganizationAdmin(admin.ModelAdmin):
    inlines = [OrganizationAdminInline]


@admin.register(models.Scheme)
class VerifierSchemeAdmin(admin.ModelAdmin):
    pass


class VerifierHostnameInline(admin.StackedInline):
    model = models.VerifierHostname
    extra = 0

    readonly_fields = (
        "dns_challenge",
        "dns_challenge_created_at",
        "dns_challenge_verified",
        "dns_challenge_verified_at",
    )


class VerifierSessionRequestInline(admin.StackedInline):
    model = models.VerifierSessionRequest
    extra = 0


@admin.register(models.Verifier)
class VerifierAdmin(admin.ModelAdmin):
    inlines = [VerifierHostnameInline, VerifierSessionRequestInline]
