import json

from django.contrib import admin
from django.utils.safestring import mark_safe

from schememanager.models.organization import OrganizationAdmin, Organization
from schememanager.models.scheme import Scheme
from schememanager.models.verifier import (
    VerifierHostname,
    VerifierSessionRequest,
    Verifier,
)


class OrganizationAdminInline(admin.StackedInline):
    model = OrganizationAdmin
    extra = 0


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    inlines = [OrganizationAdminInline]


@admin.register(Scheme)
class VerifierSchemeAdmin(admin.ModelAdmin):
    pass


class VerifierHostnameInline(admin.StackedInline):
    model = VerifierHostname
    extra = 0
    classes = ["collapse"]

    readonly_fields = (
        "dns_challenge",
        "dns_challenge_created_at",
        "dns_challenge_verified",
        "dns_challenge_verified_at",
        "dns_challenge_invalidated_at",
    )


class VerifierSessionRequestInline(admin.StackedInline):
    model = VerifierSessionRequest
    extra = 0
    classes = ["collapse"]


@admin.register(Verifier)
class VerifierAdmin(admin.ModelAdmin):
    list_filter = (
        "scheme",
        "ready",
        "reviewed_accepted",
        "scheme__production",
    )
    list_display = (
        "scheme",
        "slug",
        "name_en",
        "name_nl",
        "ready",
        "reviewed_accepted",
        "status",
    )
    list_display_links = ("scheme", "slug")

    inlines = [VerifierHostnameInline, VerifierSessionRequestInline]

    fieldsets = (
        (
            "Review",
            {
                "fields": (
                    "status",
                    "new_scheme_data_html",
                    "reviewed_accepted",
                    "rejection_remarks",
                    "approved_scheme_data_html",
                    "published_scheme_data_html",
                ),
            },
        ),
        (
            "Info",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "last_updated_at",
                    "ready",
                    "ready_at",
                    "reviewed_at",
                    "published_at",
                ),
            },
        ),
        (
            "Verifier details",
            {
                "classes": ("collapse",),
                "fields": (
                    "organization",
                    "scheme",
                    "slug",
                    "name_en",
                    "name_nl",
                    "logo",
                ),
            },
        ),
    )
    readonly_fields = [
        "status",
        "new_scheme_data_html",
        "approved_scheme_data_html",
        "published_scheme_data_html",
        "created_at",
        "last_updated_at",
        "ready",
        "ready_at",
        "reviewed_at",
        "published_at",
    ]

    def new_scheme_data_html(self, obj):
        return (
            mark_safe("<pre>" + obj.new_scheme_data_json + "\n\n" + "</pre>")
            if obj.new_scheme_data_json
            else ""
        )

    def approved_scheme_data_html(self, obj):
        return (
            mark_safe("<pre>" + obj.approved_scheme_data_json + "\n\n" + "</pre>")
            if obj.approved_scheme_data_json
            else ""
        )

    def published_scheme_data_html(self, obj):
        return (
            mark_safe("<pre>" + obj.published_scheme_data_json + "\n\n" + "</pre>")
            if obj.published_scheme_data_json
            else ""
        )
