from django.test import TestCase
from portal_backend.scheme_utils import trusted_rps_import, trusted_aps_import


class ImportTests(TestCase):
    """These tests are to make sure import utilities work as expected in the cronjobs"""

    def test_import_trusted_aps(self):
        """Test importing scheme Authentication Providers"""
        trusted_aps_import.import_aps()

    def test_import_trusted_rps(self):
        """Test importing scheme Relying Parties"""
        trusted_aps_import.import_aps()
        trusted_rps_import.import_rps()  # import rps depends on aps being imported first
