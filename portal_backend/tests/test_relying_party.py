from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from portal_backend.models.models import (
    AttestationProvider,
    Organization,
    RelyingParty,
    RelyingPartyHostname,
    Condiscon,
    CondisconAttribute,
    Credential,
    CredentialAttribute,
    TrustModel,
    YiviTrustModelEnv,
)
from portal_backend.models.models import User as OrgUser
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken  # type: ignore
from unittest.mock import patch
from django.db import IntegrityError

User = get_user_model()


class RelyingPartyCreateTest(APITestCase):
    """Ensure that a maintainer can create a relying party."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@gmail.com", username="test@gmail.com"
        )

        self.organization = Organization.objects.create(
            name_en="Test Organization",
            name_nl="Test Organization",
            slug="test-name",
            country="NL",
            house_number="2B",
            street="Test Street",
            postal_code="4321CD",
            city="Test City",
        )

        self.trust_model = TrustModel.objects.create(
            name="yivi",
            description="Trust Model Description",
            eudi_compliant=True,
        )

        self.trust_model.organizations.add(self.organization)

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
            published=True,  # published for RPs/APs
            reviewed_accepted=True,
            published_at=timezone.now(),
            created_at=timezone.now(),
            last_updated_at=timezone.now(),
        )

        self.credential = Credential.objects.create(
            attestation_provider=self.attestation_provider,
            name_en="Test Credential",
            name_nl="Test Credential",
            shortname_en="TestCred",
            shortname_nl="TestCred",
            credential_id="test-cred-id",
            should_be_singleton=True,
            issue_url="https://issue.example.com",
            description_en="Test Credential Description",
            description_nl="Test Credential Beschrijving",
        )

        self.credential_attribute = CredentialAttribute.objects.create(
            credential=self.credential,
            credential_attribute_id="attr-1",
            name_en="Test Attribute EN",
            name_nl="Test Attribute NL",
            description_en="This is the English description of the attribute.",
            description_nl="Dit is de Nederlandse beschrijving van het kenmerk.",
        )

        self.relying_party_data = {
            "rp_slug": "test-relying-party",
            "hostnames": [
                {"hostname": "test-relying-party.com"},
                {"hostname": "www.test-relying-party.com"},
            ],
            "context_description_en": "some description in English",
            "context_description_nl": "some description in Dutch",
            "environment": self.yivi_tme.environment,
            "attributes": [
                {
                    "credential_id": self.credential.id,
                    "credential_attribute_name": self.credential_attribute.name_en,
                    "reason_en": "This is the reason in English",
                    "reason_nl": "Dit is de reden in het Nederlands",
                }
            ],
        }

        self.existing_rp = RelyingParty.objects.create(
            rp_slug="existing-relying-party",
            organization=self.organization,
            yivi_tme=self.yivi_tme,
        )

        orguser = OrgUser.objects.create(email="test@gmail.com", role="maintainer")
        orguser.organizations.add(self.organization)

        token = AccessToken.for_user(self.user)
        token["organizationSlugs"] = [self.organization.slug]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token)}")

    def test_create_relying_party_success(self):
        """Test creating a relying party with valid data."""

        url = reverse("portal_backend:rp-create", args=[self.organization.slug])

        response = self.client.post(url, self.relying_party_data, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            RelyingParty.objects.filter(rp_slug="test-relying-party").exists()
        )

    def test_create_relying_party_invalid_data(self):
        """Test creating a relying party with invalid data."""
        url = reverse("portal_backend:rp-create", args=[self.organization.slug])
        invalid_data = self.relying_party_data.copy()
        invalid_data["rp_slug"] = "invalid slug"
        response = self.client.post(url, invalid_data, format="multipart")
        self.assertEqual(response.status_code, 400)

    def test_create_relying_party_rollback(self):
        url = reverse("portal_backend:rp-create", args=[self.organization.slug])

        with patch(
            "portal_backend.models.models.Condiscon.save",
            side_effect=IntegrityError("Simulated DB error"),
        ):
            response = self.client.post(url, self.relying_party_data, format="json")

            self.assertEqual(response.status_code, 500)
            self.assertFalse(
                RelyingParty.objects.filter(rp_slug="test-relying-party").exists()
            )
            self.assertFalse(
                Condiscon.objects.filter(
                    relying_party__rp_slug="test-relying-party"
                ).exists()
            )
            self.assertFalse(
                RelyingPartyHostname.objects.filter(
                    relying_party__rp_slug="test-relying-party"
                ).exists()
            )
            self.assertFalse(
                CondisconAttribute.objects.filter(
                    condiscon__relying_party__rp_slug="test-relying-party"
                ).exists()
            )

    def test_patch_relying_party_success(self):
        """Test updating a relying party with valid data."""

        url = reverse(
            "portal_backend:rp-update",
            args=[self.organization.slug, self.existing_rp.rp_slug],
        )
        patch_data = {
            "rp_slug": "updated-relying-party",
        }

        response = self.client.patch(url, patch_data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            RelyingParty.objects.get(rp_slug="updated-relying-party").rp_slug,
            "updated-relying-party",
        )

    def test_patch_relying_party_invalid_data(self):
        """Test updating a relying party with invalid data."""
        url = reverse(
            "portal_backend:rp-update",
            args=[self.organization.slug, self.existing_rp.rp_slug],
        )
        invalid_data = {
            "rp_slug": "invalid slug",
        }
        response = self.client.patch(url, invalid_data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_patch_relying_party_rollback(self):
        """Test rollback happens if error occurs with one of the fields during patch request."""
        url = reverse(
            "portal_backend:rp-update",
            args=[self.organization.slug, self.existing_rp.rp_slug],
        )

        with patch(
            "portal_backend.models.models.RelyingParty.save",
            side_effect=IntegrityError("Simulated DB error"),
        ):
            response = self.client.patch(
                url,
                {
                    "rp_slug": "updated-rp-slug",
                    "hostnames": [
                        {"hostname": "new-relying-party.com"},
                    ],
                },
                format="json",
            )

            self.assertEqual(response.status_code, 500)
            self.assertFalse(
                RelyingPartyHostname.objects.filter(
                    hostname="new-relying-party.com",
                ).exists()
            )
            self.assertEqual(
                RelyingParty.objects.get(rp_slug="existing-relying-party").rp_slug,
                "existing-relying-party",
            )

    def test_delete_relying_party_success(self):
        """Test deleting a relying party."""

        url = reverse(
            "portal_backend:rp-delete",
            args=[
                self.existing_rp.organization.slug,
                self.existing_rp.yivi_tme.environment,
                self.existing_rp.rp_slug,
            ],
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            RelyingParty.objects.filter(rp_slug="existing-relying-party").exists()
        )

    def test_delete_relying_party_not_found(self):
        """Test deleting a relying party."""

        url = reverse(
            "portal_backend:rp-delete",
            args=[
                self.existing_rp.organization.slug,
                self.existing_rp.yivi_tme.environment,
                "non-existent-slug",
            ],
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

    def test_delete_relying_party_unauthorized(self):
        """Test deleting a relying party without authorization."""
        url = reverse(
            "portal_backend:rp-delete",
            args=[
                self.existing_rp.organization.slug,
                self.existing_rp.yivi_tme.environment,
                self.existing_rp.rp_slug,
            ],
        )
        self.client.credentials()
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 401)
