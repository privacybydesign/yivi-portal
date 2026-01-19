from django.test import TestCase
from django.utils import timezone
from portal_backend.models.models import (
    AttestationProvider,
    Credential,
    CredentialAttribute,
    Organization,
    TrustModel,
    YiviTrustModelEnv,
)
from portal_backend.scheme_utils.trusted_aps_import import (
    create_credential_attributes,
    CredentialFields,
    APFields,
)
from unittest.mock import MagicMock


class CreateCredentialAttributesTest(TestCase):
    """Tests for the create_credential_attributes function in trusted_aps_import.py"""

    def setUp(self):
        self.organization = Organization.objects.create(
            name_en="Test Organization",
            name_nl="Test Organization",
            slug="test-org",
            country="NL",
            house_number="1",
            street="Test Street",
            postal_code="1234AB",
            city="Test City",
        )

        self.trust_model = TrustModel.objects.create(
            name="yivi",
            description="Trust Model Description",
            eudi_compliant=True,
        )

        self.yivi_tme = YiviTrustModelEnv.objects.create(
            trust_model=self.trust_model,
            environment="production",
            timestamp_server="https://timestamp.example.com",
            keyshare_server="https://keyshare.example.com",
            keyshare_website="https://keyshare-website.example.com",
            keyshare_attribute="test_keyshare_attribute",
            contact_website="https://contact.example.com",
            minimum_android_version="1.0",
            minimum_ios_version="1.0",
            description_en="Yivi environment description EN",
            description_nl="Yivi environment description NL",
            url="https://yivi.example.com",
        )

        self.attestation_provider = AttestationProvider.objects.create(
            organization=self.organization,
            yivi_tme=self.yivi_tme,
            version="1.0",
            shortname_en="TestAP",
            shortname_nl="TestAP",
            contact_email="ap@example.com",
            published=True,
            reviewed_accepted=True,
            published_at=timezone.now(),
            created_at=timezone.now(),
            last_updated_at=timezone.now(),
        )

        self.credential = Credential.objects.create(
            attestation_provider=self.attestation_provider,
            name_en="Test Credential",
            name_nl="Test Credential NL",
            shortname_en="TestCred",
            shortname_nl="TestCred",
            credential_id="test-cred",
            should_be_singleton=False,
            description_en="Test Credential Description",
            description_nl="Test Credential Beschrijving",
        )

    def _create_mock_cfields(self, attributes):
        """Helper to create a mock CredentialFields object with given attributes."""
        cfields = MagicMock(spec=CredentialFields)
        cfields.attributes = attributes
        return cfields

    def test_create_single_attribute(self):
        """Test creating a single credential attribute."""
        cfields = self._create_mock_cfields([
            {
                "@id": "attr1",
                "Name": {"en": "First Name", "nl": "Voornaam"},
                "Description": {"en": "Your first name", "nl": "Uw voornaam"},
                "@optional": "false",
            }
        ])

        create_credential_attributes(self.credential, cfields, "production")

        attrs = CredentialAttribute.objects.filter(credential=self.credential)
        self.assertEqual(attrs.count(), 1)
        attr = attrs.first()
        self.assertEqual(attr.name_en, "First Name")
        self.assertEqual(attr.name_nl, "Voornaam")
        self.assertEqual(attr.description_en, "Your first name")
        self.assertEqual(attr.description_nl, "Uw voornaam")
        self.assertEqual(attr.credential_attribute_tag, "attr1")
        self.assertFalse(attr.optional)

    def test_create_multiple_attributes(self):
        """Test creating multiple credential attributes."""
        cfields = self._create_mock_cfields([
            {
                "@id": "attr1",
                "Name": {"en": "First Name", "nl": "Voornaam"},
                "Description": {"en": "Your first name", "nl": "Uw voornaam"},
                "@optional": "false",
            },
            {
                "@id": "attr2",
                "Name": {"en": "Last Name", "nl": "Achternaam"},
                "Description": {"en": "Your last name", "nl": "Uw achternaam"},
                "@optional": "true",
            },
        ])

        create_credential_attributes(self.credential, cfields, "production")

        attrs = CredentialAttribute.objects.filter(credential=self.credential)
        self.assertEqual(attrs.count(), 2)

        first_name_attr = attrs.get(name_en="First Name")
        self.assertFalse(first_name_attr.optional)

        last_name_attr = attrs.get(name_en="Last Name")
        self.assertTrue(last_name_attr.optional)

    def test_skip_attribute_without_name(self):
        """Test that attributes without a Name field are skipped."""
        cfields = self._create_mock_cfields([
            {
                "@id": "attr1",
                "Description": {"en": "Incomplete attr", "nl": "Onvolledige attr"},
            },
            {
                "@id": "attr2",
                "Name": {"en": "Valid Attr", "nl": "Geldige Attr"},
                "Description": {"en": "Valid description", "nl": "Geldige beschrijving"},
            },
        ])

        create_credential_attributes(self.credential, cfields, "production")

        attrs = CredentialAttribute.objects.filter(credential=self.credential)
        self.assertEqual(attrs.count(), 1)
        self.assertEqual(attrs.first().name_en, "Valid Attr")

    def test_fallback_to_nl_name_when_en_missing(self):
        """Test that name_en falls back to nl when en is missing."""
        cfields = self._create_mock_cfields([
            {
                "@id": "attr1",
                "Name": {"nl": "Voornaam"},
                "Description": {"en": "Your first name", "nl": "Uw voornaam"},
            }
        ])

        create_credential_attributes(self.credential, cfields, "production")

        attrs = CredentialAttribute.objects.filter(credential=self.credential)
        self.assertEqual(attrs.count(), 1)
        # name_en should fall back to nl value
        self.assertEqual(attrs.first().name_en, "Voornaam")

    def test_delete_removed_attributes(self):
        """Test that attributes no longer in the source scheme are deleted."""
        # First, create some existing attributes
        CredentialAttribute.objects.create(
            credential=self.credential,
            credential_attribute_tag="old-attr1",
            name_en="Old Attribute 1",
            name_nl="Oud Attribuut 1",
            description_en="Old description 1",
            description_nl="Oude beschrijving 1",
        )
        CredentialAttribute.objects.create(
            credential=self.credential,
            credential_attribute_tag="old-attr2",
            name_en="Old Attribute 2",
            name_nl="Oud Attribuut 2",
            description_en="Old description 2",
            description_nl="Oude beschrijving 2",
        )

        self.assertEqual(
            CredentialAttribute.objects.filter(credential=self.credential).count(), 2
        )

        # Now import with only one new attribute (the old ones should be deleted)
        cfields = self._create_mock_cfields([
            {
                "@id": "new-attr1",
                "Name": {"en": "New Attribute", "nl": "Nieuw Attribuut"},
                "Description": {"en": "New description", "nl": "Nieuwe beschrijving"},
            }
        ])

        create_credential_attributes(self.credential, cfields, "production")

        attrs = CredentialAttribute.objects.filter(credential=self.credential)
        self.assertEqual(attrs.count(), 1)
        self.assertEqual(attrs.first().name_en, "New Attribute")

    def test_keep_existing_attributes_when_still_in_source(self):
        """Test that existing attributes are kept when they're still in the source."""
        # Create an existing attribute
        CredentialAttribute.objects.create(
            credential=self.credential,
            credential_attribute_tag="existing-attr",
            name_en="Existing Attribute",
            name_nl="Bestaand Attribuut",
            description_en="Existing description",
            description_nl="Bestaande beschrijving",
        )

        # Import with the same attribute (should be updated, not deleted)
        cfields = self._create_mock_cfields([
            {
                "@id": "existing-attr",
                "Name": {"en": "Existing Attribute", "nl": "Bestaand Attribuut"},
                "Description": {
                    "en": "Updated description",
                    "nl": "Bijgewerkte beschrijving",
                },
            }
        ])

        create_credential_attributes(self.credential, cfields, "production")

        attrs = CredentialAttribute.objects.filter(credential=self.credential)
        self.assertEqual(attrs.count(), 1)
        attr = attrs.first()
        self.assertEqual(attr.name_en, "Existing Attribute")
        self.assertEqual(attr.description_en, "Updated description")

    def test_partial_attribute_removal(self):
        """Test that only some attributes are removed when source has fewer."""
        # Create three existing attributes
        CredentialAttribute.objects.create(
            credential=self.credential,
            credential_attribute_tag="attr1",
            name_en="Attribute One",
            name_nl="Attribuut Een",
            description_en="Description 1",
            description_nl="Beschrijving 1",
        )
        CredentialAttribute.objects.create(
            credential=self.credential,
            credential_attribute_tag="attr2",
            name_en="Attribute Two",
            name_nl="Attribuut Twee",
            description_en="Description 2",
            description_nl="Beschrijving 2",
        )
        CredentialAttribute.objects.create(
            credential=self.credential,
            credential_attribute_tag="attr3",
            name_en="Attribute Three",
            name_nl="Attribuut Drie",
            description_en="Description 3",
            description_nl="Beschrijving 3",
        )

        self.assertEqual(
            CredentialAttribute.objects.filter(credential=self.credential).count(), 3
        )

        # Import with only two attributes (Attribute One and Attribute Three)
        cfields = self._create_mock_cfields([
            {
                "@id": "attr1",
                "Name": {"en": "Attribute One", "nl": "Attribuut Een"},
                "Description": {"en": "Description 1", "nl": "Beschrijving 1"},
            },
            {
                "@id": "attr3",
                "Name": {"en": "Attribute Three", "nl": "Attribuut Drie"},
                "Description": {"en": "Description 3", "nl": "Beschrijving 3"},
            },
        ])

        create_credential_attributes(self.credential, cfields, "production")

        attrs = CredentialAttribute.objects.filter(credential=self.credential)
        self.assertEqual(attrs.count(), 2)
        attr_names = list(attrs.values_list("name_en", flat=True))
        self.assertIn("Attribute One", attr_names)
        self.assertIn("Attribute Three", attr_names)
        self.assertNotIn("Attribute Two", attr_names)

    def test_empty_attributes_deletes_all(self):
        """Test that all attributes are deleted when source has none."""
        # Create existing attributes
        CredentialAttribute.objects.create(
            credential=self.credential,
            credential_attribute_tag="attr1",
            name_en="Attribute 1",
            name_nl="Attribuut 1",
            description_en="Description 1",
            description_nl="Beschrijving 1",
        )
        CredentialAttribute.objects.create(
            credential=self.credential,
            credential_attribute_tag="attr2",
            name_en="Attribute 2",
            name_nl="Attribuut 2",
            description_en="Description 2",
            description_nl="Beschrijving 2",
        )

        self.assertEqual(
            CredentialAttribute.objects.filter(credential=self.credential).count(), 2
        )

        # Import with empty attributes list
        cfields = self._create_mock_cfields([])

        create_credential_attributes(self.credential, cfields, "production")

        attrs = CredentialAttribute.objects.filter(credential=self.credential)
        self.assertEqual(attrs.count(), 0)

    def test_does_not_delete_attributes_of_other_credentials(self):
        """Test that deletion only affects the target credential's attributes."""
        # Create another credential
        other_credential = Credential.objects.create(
            attestation_provider=self.attestation_provider,
            name_en="Other Credential",
            name_nl="Andere Credential",
            shortname_en="OtherCred",
            shortname_nl="OtherCred",
            credential_id="other-cred",
            should_be_singleton=False,
            description_en="Other Credential Description",
            description_nl="Andere Credential Beschrijving",
        )

        # Create attributes for both credentials
        CredentialAttribute.objects.create(
            credential=self.credential,
            credential_attribute_tag="attr1",
            name_en="Main Attr",
            name_nl="Hoofd Attr",
            description_en="Main description",
            description_nl="Hoofd beschrijving",
        )
        CredentialAttribute.objects.create(
            credential=other_credential,
            credential_attribute_tag="attr1",
            name_en="Other Attr",
            name_nl="Andere Attr",
            description_en="Other description",
            description_nl="Andere beschrijving",
        )

        # Import with empty attributes for main credential
        cfields = self._create_mock_cfields([])

        create_credential_attributes(self.credential, cfields, "production")

        # Main credential should have no attributes
        self.assertEqual(
            CredentialAttribute.objects.filter(credential=self.credential).count(), 0
        )
        # Other credential should still have its attribute
        self.assertEqual(
            CredentialAttribute.objects.filter(credential=other_credential).count(), 1
        )

    def test_default_description_when_missing(self):
        """Test that default description is used when not provided."""
        cfields = self._create_mock_cfields([
            {
                "@id": "attr1",
                "Name": {"en": "Test Attr", "nl": "Test Attr NL"},
            }
        ])

        create_credential_attributes(self.credential, cfields, "production")

        attrs = CredentialAttribute.objects.filter(credential=self.credential)
        self.assertEqual(attrs.count(), 1)
        attr = attrs.first()
        self.assertEqual(attr.description_en, "No description provided")
        self.assertEqual(attr.description_nl, "No description provided")
