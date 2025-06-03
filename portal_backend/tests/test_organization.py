import os
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from portal_backend.models.models import Organization
from portal_backend.models.models import User as OrgUser
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from portal_backend.scheme_utils.import_utils import load_logo_if_exists
from rest_framework_simplejwt.tokens import AccessToken  # type: ignore
from unittest.mock import patch
from django.db import IntegrityError


User = get_user_model()


class OrganizationCreateTest(APITestCase):
    """Ensure that an authenticated user can create an organization."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@gmail.com", username="test@gmail.com"
        )
        self.client.force_authenticate(user=self.user)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.logo_path = os.path.join(current_dir, "test_logo.png")
        self.logo = load_logo_if_exists(self.logo_path)

        self.organization_data = {
            "name_en": "Test Organization",
            "name_nl": "Test Organisatie",
            "slug": "test-organization",
            "registration_number": "123456789",
            "country": "NL",
            "house_number": "1A",
            "street": "Test Street",
            "postal_code": "1234AB",
            "city": "Test City",
            "logo": self.logo,
        }

    def test_create_organization_created(self):
        """Test creating an organization with valid data."""
        url = reverse("portal_backend:organization-create")

        response = self.client.post(url, self.organization_data, format="multipart")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            Organization.objects.filter(name_en="Test Organization").exists()
        )
        self.assertTrue(
            OrgUser.objects.filter(email="test@gmail.com", role="maintainer").exists()
        )

    def test_create_organization_invalid_data(self):
        """Test creating an organization with invalid data."""
        url = reverse("portal_backend:organization-create")
        invalid_data = self.organization_data.copy()
        invalid_data["slug"] = "invalid slug"
        response = self.client.post(url, invalid_data, format="multipart")
        self.assertEqual(response.status_code, 400)

    def test_create_organization_rollback(self):
        """Test rollback happens if error occurs during post request in view."""
        url = reverse("portal_backend:organization-create")

        with patch(
            "portal_backend.models.models.User.save",
            side_effect=IntegrityError("Simulated DB error"),
        ):
            response = self.client.post(url, self.organization_data, format="multipart")

            self.assertEqual(response.status_code, 500)
            self.assertFalse(
                Organization.objects.filter(name_en="Test Organization").exists()
            )


class OrganizationMaintainerActionsTest(APITestCase):
    """Ensure that an authenticated user can update an organization."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@gmail.com", username="test@gmail.com"
        )
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.logo_path = os.path.join(current_dir, "test_logo.png")
        self.logo = load_logo_if_exists(self.logo_path)
        self.organization = Organization.objects.create(
            name_en="Test Organization",
            name_nl="Test Organization",
            slug="test-name",
            registration_number="987654321",
            country="NL",
            house_number="2B",
            street="Test Street",
            postal_code="4321CD",
            city="Test City",
            logo=self.logo,
        )
        orguser = OrgUser.objects.create(email="test@gmail.com", role="maintainer")
        orguser.organizations.add(self.organization)
        token = AccessToken.for_user(self.user)
        token["organizationSlugs"] = [self.organization.slug]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(token)}")

    def test_patch_organization_success(self):
        """Test updating an organization with valid data."""

        url = reverse(
            "portal_backend:organization-update", args=[self.organization.slug]
        )
        response = self.client.patch(
            url,
            {
                "name_en": "Updated Name",
            },
            format="multipart",
        )
        self.organization.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.organization.name_en, "Updated Name")

    def test_add_maintainer_created(self):
        """Test adding a maintainer to an organization."""
        url = reverse(
            "portal_backend:organization-maintainers", args=[self.organization.slug]
        )
        response = self.client.post(
            url,
            {"email": "testemail@gmail.com"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            OrgUser.objects.filter(
                email="testemail@gmail.com", role="maintainer"
            ).exists()
        )

    def test_add_maintainer_invalid_email(self):
        """Test should fail when adding a maintainer with an invalid email."""
        url = reverse(
            "portal_backend:organization-maintainers", args=[self.organization.slug]
        )
        response = self.client.post(
            url,
            {"email": "invalid-email"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_maintainer_success(self):
        """Test removing a maintainer from an organization."""
        maintainer = OrgUser.objects.create(email="test@test.com", role="maintainer")
        maintainer.organizations.add(self.organization)
        url = reverse(
            "portal_backend:organization-maintainers",
            args=[self.organization.slug, maintainer.id],
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            not OrgUser.objects.filter(
                email="test@test.com", role="maintainer"
            ).exists()
        )

    def test_delete_maintainer_forbidden(self):
        """Test that a maintainer cannot delete other organization's maintainers."""
        other_org = Organization.objects.create(
            name_en="Other Organization",
            name_nl="Andere Organisatie",
            slug="other-organization",
            registration_number="123456789",
            country="NL",
            house_number="1A",
            street="Other Street",
            postal_code="1234AB",
            city="Other City",
            logo=self.logo,
        )
        maintainer = OrgUser.objects.create(email="test@email.com", role="maintainer")
        maintainer.organizations.add(other_org)
        url = reverse(
            "portal_backend:organization-maintainers",
            args=[other_org.slug, maintainer.id],
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 403)

    def test_patch_organization_rollback(self):
        """Test rollback happens if error occurs during patch request."""
        url = reverse(
            "portal_backend:organization-update", args=[self.organization.slug]
        )
        with patch(
            "portal_backend.models.models.Organization.save",
            side_effect=IntegrityError("Simulated DB error"),
        ):
            response = self.client.patch(
                url,
                {
                    "name_en": "Test",
                },
                format="multipart",
            )

            self.assertFalse(Organization.objects.filter(name_en="Test").exists())

    def test_add_maintainer_duplicate(self):
        """Test rollback happens if error occurs during adding organizations to user."""
        url = reverse(
            "portal_backend:organization-maintainers", args=[self.organization.slug]
        )

        user = OrgUser.objects.create(
            email="newmaintainer@gmail.com", role="maintainer"
        )

        with patch.object(
            user.organizations, "add", side_effect=IntegrityError("Simulated DB error")
        ):
            response = self.client.post(
                url,
                {"email": "newmaintainer@gmail.com"},
                format="json",
            )

            self.assertEqual(response.status_code, 400)
            self.assertFalse(
                user.organizations.filter(slug=self.organization.slug).exists()
            )
