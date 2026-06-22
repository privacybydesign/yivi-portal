from django.test import TestCase
from portal_backend.scheme_utils import trusted_rps_import, trusted_aps_import
from portal_backend.models.models import (
    Organization,
    RelyingParty,
    RelyingPartyHostname,
    TrustModel,
    YiviTrustModelEnv,
)


class ImportTests(TestCase):
    """These tests are to make sure import utilities work as expected in the cronjobs"""

    def test_import_trusted_aps(self):
        """Test importing scheme Authentication Providers"""
        trusted_aps_import.import_aps()

    def test_import_trusted_rps(self):
        """Test importing scheme Relying Parties"""
        trusted_aps_import.import_aps()
        trusted_rps_import.import_rps()  # import rps depends on aps being imported first


class DeleteStaleHostnamesTest(TestCase):
    """The requestor-sync cron must remove hostnames that are no longer present
    in the latest scheme pull, so local state matches the scheme."""

    def setUp(self):
        self.organization = Organization.objects.create(
            name_en="Test Organization",
            name_nl="Test Organization",
            slug="test-rp",
        )
        self.trust_model = TrustModel.objects.create(
            name="yivi",
            description="Trust Model Description",
            eudi_compliant=False,
        )
        self.yivi_tme = YiviTrustModelEnv.objects.create(
            trust_model=self.trust_model,
            environment="production",
        )
        self.rp = RelyingParty.objects.create(
            organization=self.organization,
            yivi_tme=self.yivi_tme,
            rp_slug="test-rp",
        )

    def _make_hostname(self, hostname):
        return RelyingPartyHostname.objects.create(
            hostname=hostname,
            relying_party=self.rp,
            manually_verified=True,
        )

    def test_stale_hostname_is_deleted(self):
        """A hostname absent from the latest scheme pull is removed, while
        hostnames still in the scheme are kept."""
        self._make_hostname("kept.example.com")
        self._make_hostname("stale.example.com")

        # The scheme now only lists the "kept" hostname.
        trusted_rps_import.delete_stale_hostnames(
            self.rp, ["kept.example.com"], self.rp.rp_slug
        )

        remaining = set(self.rp.hostnames.values_list("hostname", flat=True))
        self.assertEqual(remaining, {"kept.example.com"})
        self.assertFalse(
            RelyingPartyHostname.objects.filter(hostname="stale.example.com").exists()
        )

    def test_no_deletion_when_all_hostnames_present(self):
        """Nothing is removed when every local hostname is still in the scheme."""
        self._make_hostname("a.example.com")
        self._make_hostname("b.example.com")

        trusted_rps_import.delete_stale_hostnames(
            self.rp, ["a.example.com", "b.example.com"], self.rp.rp_slug
        )

        self.assertEqual(self.rp.hostnames.count(), 2)

    def test_create_hostnames_removes_stale(self):
        """create_hostnames adds the scheme hostnames and prunes the rest in one pass."""
        self._make_hostname("old.example.com")

        class _Fields:
            slug = "test-rp"
            hostnames = ["new.example.com"]

        trusted_rps_import.create_hostnames(_Fields(), self.rp)

        remaining = set(self.rp.hostnames.values_list("hostname", flat=True))
        self.assertEqual(remaining, {"new.example.com"})

    def test_stale_hostname_of_other_rp_is_untouched(self):
        """Pruning is scoped to the RP being synced and never touches another RP."""
        other_org = Organization.objects.create(
            name_en="Other", name_nl="Other", slug="other-rp"
        )
        other_rp = RelyingParty.objects.create(
            organization=other_org,
            yivi_tme=self.yivi_tme,
            rp_slug="other-rp",
        )
        RelyingPartyHostname.objects.create(
            hostname="other.example.com",
            relying_party=other_rp,
            manually_verified=True,
        )
        self._make_hostname("stale.example.com")

        trusted_rps_import.delete_stale_hostnames(self.rp, [], self.rp.rp_slug)

        self.assertTrue(
            RelyingPartyHostname.objects.filter(hostname="other.example.com").exists()
        )
        self.assertFalse(
            RelyingPartyHostname.objects.filter(hostname="stale.example.com").exists()
        )
