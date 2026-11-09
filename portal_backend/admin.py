import math
from datetime import date
from typing import ClassVar

from django import forms
from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.core.exceptions import PermissionDenied, ValidationError
from django.template.response import TemplateResponse
from django.utils import timezone

from portal_backend.models.models import (
    AttestationProvider,
    Condiscon,
    CondisconAttribute,
    Credential,
    CredentialAttribute,
    Organization,
    RelyingParty,
    RelyingPartyHostname,
    TrustedVerifierUsage,
    TrustModel,
    UsageReport,
    UsageServerKey,
    User,
    YiviTrustModelEnv,
)
from portal_backend.services import usage


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
        return obj.credential.full_path + "." + obj.credential_attribute_tag


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name_en", "created_at", "last_updated_at")
    search_fields = ("name_en", "name_nl")
    list_filter = ("created_at", "last_updated_at")
    prepopulated_fields: ClassVar[dict] = {"slug": ("name_en",)}
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
    search_fields: ClassVar[list] = ["name_en"]

    def get_full_path(self, obj):
        return obj.full_path

    get_full_path.short_description = "Credential Identifier"


class CondisconAttributeInline(admin.TabularInline):
    model = CondisconAttribute
    extra = 1
    autocomplete_fields: ClassVar[list] = ["credential_attribute"]


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


def _axis(max_count: int) -> list[int]:
    """A round axis maximum in four whole-number steps, e.g. 37 -> 0, 10, 20, 30, 40."""
    if max_count <= 0:
        return [0, 1, 2, 3, 4]
    raw_step = max_count / 4
    magnitude = 10 ** math.floor(math.log10(raw_step))
    step = next(
        (m * magnitude for m in (1, 2, 2.5, 5, 10) if m * magnitude >= raw_step),
        10 * magnitude,
    )
    step = max(1, math.ceil(step))
    return [i * step for i in range(5)]


def _shift_month(year: int, month: int, step: int) -> tuple[int, int]:
    index = year * 12 + (month - 1) + step
    return index // 12, index % 12 + 1


def usage_chart_context(request, reports) -> dict:
    """The admin's usage chart: successful verifications per day of one calendar
    month (``?month=YYYY-MM``, the current month by default), and the runs."""
    today = timezone.localdate()
    try:
        year, month = (int(part) for part in request.GET.get("month", "").split("-"))
        date(year, month, 1)
    except (ValueError, OverflowError):
        # date() raises OverflowError for a year that does not fit a C int.
        year, month = today.year, today.month
    if (year, month) > (today.year, today.month):
        year, month = today.year, today.month

    days = usage.daily_verifications(reports, year, month)
    ticks = _axis(max(d["count"] for d in days))
    top = ticks[-1]
    previous = _shift_month(year, month, -1)
    following = _shift_month(year, month, 1)
    return {
        "month": date(year, month, 1),
        "total": sum(d["count"] for d in days),
        "days": [
            {**d, "height": round(d["count"] / top * 100, 2), "label": d["day"].day}
            for d in days
        ],
        "ticks": [{"value": t, "bottom": round(t / top * 100, 2)} for t in ticks],
        "previous_month": "%04d-%02d" % previous,
        "next_month": (
            "%04d-%02d" % following if following <= (today.year, today.month) else None
        ),
        "runs": usage.run_overview(reports),
    }


class UsageServerKeyForm(forms.ModelForm):
    """Checks the key before save, so a bad or duplicate key is a form error, not a 500.

    The thumbprint is read-only in the admin, so its uniqueness is checked here.
    """

    class Meta:
        model = UsageServerKey
        fields = ("organization", "label", "public_key_pem", "deactivated_at")

    def clean_public_key_pem(self):
        try:
            key = usage.public_key_from_pem(self.cleaned_data["public_key_pem"])
        except ValueError as e:
            raise ValidationError(str(e)) from e
        duplicates = UsageServerKey.objects.filter(thumbprint=usage.thumbprint(key))
        if not self.instance._state.adding:
            duplicates = duplicates.exclude(pk=self.instance.pk)
        if duplicates.exists():
            raise ValidationError("This key is already registered.")
        return usage.pem_from_public_key(key)


@admin.register(UsageServerKey)
class UsageServerKeyAdmin(admin.ModelAdmin):
    form = UsageServerKeyForm
    list_display = (
        "organization",
        "label",
        "thumbprint",
        "created_at",
        "deactivated_at",
    )
    search_fields = ("organization__slug", "label", "thumbprint")
    readonly_fields = ("thumbprint",)
    change_form_template = "admin/portal_backend/usageserverkey/change_form.html"

    def change_view(self, request, object_id, form_url="", extra_context=None):
        server_key = self.get_object(request, unquote(object_id))
        if server_key is not None:
            extra_context = {
                **(extra_context or {}),
                "usage": usage_chart_context(request, server_key.reports.all()),
            }
        return super().change_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        # The thumbprint is how a server finds its account, so it always follows the key.
        obj.thumbprint = usage.thumbprint(usage.public_key_from_pem(obj.public_key_pem))
        super().save_model(request, obj, form, change)


@admin.register(UsageReport)
class UsageReportAdmin(admin.ModelAdmin):
    list_display = (
        "server_key",
        "server_instance",
        "run_id",
        "sequence",
        "final",
        "period_to",
        "received_at",
    )
    list_filter = ("final",)
    search_fields = ("server_key__organization__slug", "server_instance", "run_id")


TRUSTED_VERIFIER_STATUS_LABELS = {
    "no_key": "No usage key",
    "no_reports": "No reports yet",
    "host_not_reported": "Hostname not reported",
    "silent": "Silent",
    "reporting": "Reporting",
}


@admin.register(TrustedVerifierUsage)
class TrustedVerifierUsageAdmin(admin.ModelAdmin):
    """Per hostname of a Trusted Verifier, whether its usage reports arrive.

    Read-only: the page shows usage.trusted_verifier_usage() instead of a list of model rows.
    """

    change_list_template = "admin/portal_backend/trustedverifierusage/change_list.html"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        if not self.has_view_permission(request):
            raise PermissionDenied
        rows = usage.trusted_verifier_usage()
        for row in rows:
            row["status_label"] = TRUSTED_VERIFIER_STATUS_LABELS[row["status"]]
        silence_hours = int(usage.TRUSTED_VERIFIER_SILENCE.total_seconds() // 3600)
        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Trusted Verifier usage",
            "rows": rows,
            "attention": sum(1 for r in rows if r["status"] != "reporting"),
            "silence_hours": silence_hours,
            "status_labels": TRUSTED_VERIFIER_STATUS_LABELS,
            **(extra_context or {}),
        }
        return TemplateResponse(request, self.change_list_template, context)
