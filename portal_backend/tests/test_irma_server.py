import os
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from portal_backend.models.models import IrmaServer
from django.contrib.auth import get_user_model
from portal_backend.scheme_utils.import_utils import load_logo_if_exists

User = get_user_model()

TEST_MAIL = "test@gmail.com"
INVALID_MAIL = "invalid-email-format"
VERSION = "1.0.0"

class IrmaServerCreateTest(APITestCase):
    """Ensure that an authenticated user can create an Irma Server."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email=TEST_MAIL, username=TEST_MAIL
        )
        self.client.force_authenticate(user=self.user)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.logo_path = os.path.join(current_dir, "test_logo.png")
        self.logo = load_logo_if_exists(self.logo_path)
        self.client.credentials(HTTP_USER_AGENT='IrmaServer')

        self.irma_server_data = {
            "email": TEST_MAIL,
            "version": VERSION,
        }
    
    def test_create_irma_server(self):
        url = reverse("portal_backend:irma-server-create")

        response = self.client.post(url, self.irma_server_data, format="multipart")
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            IrmaServer.objects.filter(email=TEST_MAIL, version=VERSION).exists()
        )

    def test_create_irma_server_invalid_data(self):
        """Test creating an Irma Server with invalid data."""
        url = reverse("portal_backend:irma-server-create")
        invalid_data = self.irma_server_data.copy()
        invalid_data["email"] = INVALID_MAIL
        response = self.client.post(url, invalid_data, format="multipart")
        self.assertEqual(response.status_code, 400)
        
    def test_create_irma_server_missing_data(self):
        """Test creating an Irma Server with missing data."""
        url = reverse("portal_backend:irma-server-create")
        incomplete_data = {
            "email": TEST_MAIL,
            # "version" is missing
        }
        response = self.client.post(url, incomplete_data, format="multipart")
        self.assertEqual(response.status_code, 400)
        self.assertIn("version", response.data)

    def test_create_irma_server_unauthenticated(self):
        """Test that unauthenticated users cannot create an Irma Server."""
        self.client.force_authenticate(user=None)  # Log out the user
        url = reverse("portal_backend:irma-server-create")
        response = self.client.post(url, self.irma_server_data, format="multipart")
        self.assertEqual(response.status_code, 401)

    def test_create_irma_server_invalid_user_agent(self):
        """Test creating an Irma Server with an invalid User-Agent header."""
        url = reverse("portal_backend:irma-server-create")
        self.client.credentials(HTTP_USER_AGENT='InvalidAgent')
        response = self.client.post(url, self.irma_server_data, format="multipart")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid User-Agent", response.data.get("error", ""))