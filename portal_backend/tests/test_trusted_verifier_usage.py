from datetime import timedelta

from cryptography.hazmat.primitives.asymmetric import ec
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from portal_backend.models.models import (
    Organization,
    RelyingParty,
    RelyingPartyHostname,
    TrustModel,
    UsageReport,
    UsageSessionCount,
    YiviTrustModelEnv,
)
from portal_backend.services import usage
from portal_backend.tests.test_usage import make_report, public_pem


def trust_model_env(environment: str) -> YiviTrustModelEnv:
    trust_model, _ = TrustModel.objects.get_or_create(
        name="yivi", defaults={"description": "Yivi", "eudi_compliant": False}
    )
    return YiviTrustModelEnv.objects.create(
        trust_model=trust_model,
        environment=environment,
        timestamp_server="https://timestamp.example.com",
        keyshare_server="https://keyshare.example.com",
        keyshare_website="https://keyshare-website.example.com",
        keyshare_attribute="test_keyshare_attribute",
        contact_website="https://contact.example.com",
        minimum_android_version="1.0",
        minimum_ios_version="1.0",
        description_en="Yivi",
        description_nl="Yivi",
        url="https://yivi.example.com",
    )


def report_with_host(report_id: str, host: str | None) -> dict:
    report = make_report(report_id)
    if host is not None:
        for row in report["sessions"] + report["disclosures"]:
            row["host"] = host
    return report


class TrustedVerifierUsageTest(TestCase):
    """Whether the usage of every Trusted Verifier hostname is reported."""

    def setUp(self):
        self.production = trust_model_env("production")
        self.organization = Organization.objects.create(
            name_en="Gemeente", name_nl="Gemeente", slug="gemeente", is_verified=True
        )
        self.add_relying_party(
            self.organization, "gemeente", ["irma.gemeente.nl", "irma-acc.gemeente.nl"]
        )

    def add_relying_party(
        self, organization, slug, hostnames, published=True, env=None, required=True
    ):
        relying_party = RelyingParty.objects.create(
            rp_slug=slug,
            organization=organization,
            yivi_tme=env or self.production,
            published=published,
            usage_reporting_required=required,
        )
        for hostname in hostnames:
            RelyingPartyHostname.objects.create(
                hostname=hostname, relying_party=relying_party
            )
        return relying_party

    def add_key(self, organization):
        return usage.register_key(
            organization, public_pem(ec.generate_private_key(ec.SECP256R1()))
        )

    def statuses(self, now=None):
        return {
            row["hostname"]: row["status"]
            for row in usage.trusted_verifier_usage(now=now)
        }

    def test_no_key(self):
        self.assertEqual(
            self.statuses(),
            {"irma.gemeente.nl": "no_key", "irma-acc.gemeente.nl": "no_key"},
        )

    def test_no_reports(self):
        self.add_key(self.organization)
        self.assertEqual(self.statuses()["irma.gemeente.nl"], "no_reports")

    def test_reports_without_host(self):
        # A server on irmago 1.5.0 reports, but without hosts.
        usage.store_report(
            self.add_key(self.organization), report_with_host("r1", None)
        )
        self.assertEqual(self.statuses()["irma.gemeente.nl"], "host_not_reported")

    def test_reporting_per_hostname(self):
        usage.store_report(
            self.add_key(self.organization), report_with_host("r1", "IRMA.gemeente.nl")
        )
        # The hostname is matched case-insensitively; the acceptance server does not report.
        self.assertEqual(
            self.statuses(),
            {
                "irma.gemeente.nl": "reporting",
                "irma-acc.gemeente.nl": "host_not_reported",
            },
        )

    def test_silent(self):
        key = self.add_key(self.organization)
        usage.store_report(key, report_with_host("r1", "irma.gemeente.nl"))
        UsageReport.objects.update(received_at=timezone.now() - timedelta(hours=25))
        self.assertEqual(self.statuses()["irma.gemeente.nl"], "silent")

        # A key deactivated later does not hide that the hostname reported before.
        key.deactivated_at = timezone.now()
        key.save(update_fields=["deactivated_at"])
        self.assertEqual(self.statuses()["irma.gemeente.nl"], "silent")

    def test_reported_by_a_hosting_party(self):
        host = Organization.objects.create(
            name_en="Hoster", name_nl="Hoster", slug="hoster", is_verified=True
        )
        usage.store_report(
            self.add_key(host), report_with_host("r1", "irma.gemeente.nl")
        )
        self.assertEqual(self.statuses()["irma.gemeente.nl"], "reporting")

    def test_only_published_production_relying_parties_that_must_report(self):
        other = Organization.objects.create(
            name_en="Other", name_nl="Ander", slug="other"
        )
        self.add_relying_party(other, "draft", ["draft.example.com"], published=False)
        self.add_relying_party(
            other, "staging", ["staging.example.com"], env=trust_model_env("staging")
        )
        # The contract of this Trusted Verifier does not require usage reporting.
        self.add_relying_party(
            other, "no-contract", ["irma.other.example.com"], required=False
        )
        self.assertEqual(
            set(self.statuses()), {"irma.gemeente.nl", "irma-acc.gemeente.nl"}
        )

    def test_attention_first(self):
        usage.store_report(
            self.add_key(self.organization), report_with_host("r1", "irma.gemeente.nl")
        )
        rows = usage.trusted_verifier_usage()
        self.assertEqual(
            [r["status"] for r in rows], ["host_not_reported", "reporting"]
        )
        self.assertEqual(rows[1]["active_keys"], 1)
        self.assertIsNotNone(rows[1]["host_last_report_at"])


class ReportHostTest(TestCase):
    def setUp(self):
        organization = Organization.objects.create(
            name_en="Webshop", name_nl="Webwinkel", slug="webshop", is_verified=True
        )
        self.key = usage.register_key(
            organization, public_pem(ec.generate_private_key(ec.SECP256R1()))
        )

    def test_stores_the_host_of_each_row(self):
        report, _ = usage.store_report(
            self.key, report_with_host("r1", "Irma.Example.com")
        )
        self.assertEqual(
            set(report.sessions.values_list("host", flat=True)), {"irma.example.com"}
        )
        self.assertEqual(
            set(report.disclosures.values_list("host", flat=True)), {"irma.example.com"}
        )

    def test_host_is_optional(self):
        report, _ = usage.store_report(self.key, report_with_host("r1", None))
        self.assertEqual(set(report.sessions.values_list("host", flat=True)), {""})

    def test_rejects_an_invalid_host(self):
        with self.assertRaises(usage.UsageProblem):
            usage.store_report(self.key, report_with_host("r1", ["irma.example.com"]))
        self.assertFalse(UsageSessionCount.objects.exists())


class TrustedVerifierUsageAdminTest(TestCase):
    def setUp(self):
        from yivi_portal.admin_site import VERIFIED_SESSION_KEY

        organization = Organization.objects.create(
            name_en="Gemeente", name_nl="Gemeente", slug="gemeente", is_verified=True
        )
        relying_party = RelyingParty.objects.create(
            rp_slug="gemeente",
            organization=organization,
            yivi_tme=trust_model_env("production"),
            published=True,
            usage_reporting_required=True,
        )
        RelyingPartyHostname.objects.create(
            hostname="irma.gemeente.nl", relying_party=relying_party
        )
        admin_user = get_user_model().objects.create_superuser(
            username="admin@yivi.app", email="admin@yivi.app", password="x"
        )
        self.client.force_login(admin_user)
        session = self.client.session
        session[VERIFIED_SESSION_KEY] = str(admin_user.pk)
        session.save()
        self.url = reverse("admin:portal_backend_trustedverifierusage_changelist")

    def test_lists_the_hostnames_and_their_status(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "irma.gemeente.nl")
        self.assertContains(response, "No usage key")
        self.assertContains(response, "1 of 1 hostname needs attention.")

    def test_is_read_only(self):
        response = self.client.get(
            reverse("admin:portal_backend_trustedverifierusage_add")
        )
        self.assertEqual(response.status_code, 403)
