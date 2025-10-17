import os
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from portal_backend.models.models import IrmaServer
from django.contrib.auth import get_user_model
from portal_backend.scheme_utils.import_utils import load_logo_if_exists

User = get_user_model()

TEST_MAIL = "test@gmail.com"
TEST_MAIL2 = "test2@gmail.com"
INVALID_MAIL = "invalid-email-format"
VERSION = "1.0.0"
VERSION2 = "2.0.0"

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

class IrmaServerListTest(APITestCase):
    """Ensure that an authenticated user can list Irma Servers."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email=TEST_MAIL, username=TEST_MAIL
        )
        self.client.force_authenticate(user=self.user)

        # Create some IrmaServer instances for testing
        IrmaServer.objects.create(email=TEST_MAIL, version=VERSION)
        IrmaServer.objects.create(email=TEST_MAIL2, version=VERSION2)

    def test_list_irma_servers(self):
        url = reverse("portal_backend:irma-server-list")

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        emails = [irma_server["email"] for irma_server in response.data]
        self.assertIn(TEST_MAIL, emails)
        self.assertIn(TEST_MAIL2, emails)

class IrmaServerDetailTest(APITestCase):
    """Ensure that an authenticated user can retrieve an Irma Server by ID."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email=TEST_MAIL, username=TEST_MAIL
        )
        self.client.force_authenticate(user=self.user)

        # Create an IrmaServer instance for testing
        self.irma_server = IrmaServer.objects.create(email=TEST_MAIL, version=VERSION)

    def test_retrieve_irma_server(self):
        url = reverse("portal_backend:irma-server-detail", args=[self.irma_server.id])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], TEST_MAIL)
        self.assertEqual(response.data["version"], VERSION)

    def test_retrieve_irma_server_not_found(self):
        url = reverse("portal_backend:irma-server-detail", args=[9999])  # Non-existent ID

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class IrmaServerUpdateTest(APITestCase):
    """Ensure that an authenticated user can update an Irma Server."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email=TEST_MAIL, username=TEST_MAIL
        )
        self.client.force_authenticate(user=self.user)

        # Create an IrmaServer instance for testing
        self.irma_server = IrmaServer.objects.create(email=TEST_MAIL, version=VERSION)

    def test_update_irma_server(self):
        url = reverse("portal_backend:irma-server-update", args=[self.irma_server.id])
        updated_data = {
            "email": TEST_MAIL2,
            "version": VERSION2,
        }

        response = self.client.put(url, updated_data, format="multipart")
        self.assertEqual(response.status_code, 200)
        self.irma_server.refresh_from_db()
        self.assertEqual(self.irma_server.email, TEST_MAIL2)
        self.assertEqual(self.irma_server.version, VERSION2)

    def test_update_irma_server_not_found(self):
        url = reverse("portal_backend:irma-server-update", args=[9999])  # Non-existent ID
        updated_data = {
            "email": TEST_MAIL2,
            "version": VERSION2,
        }

        response = self.client.put(url, updated_data, format="multipart")
        self.assertEqual(response.status_code, 404)

    def test_update_irma_server_invalid_data(self):
        url = reverse("portal_backend:irma-server-update", args=[self.irma_server.id])
        invalid_data = {
            "email": INVALID_MAIL,
            "version": VERSION2,
        }

        response = self.client.put(url, invalid_data, format="multipart")
        self.assertEqual(response.status_code, 400)

class IrmaServerDeleteTest(APITestCase):
    """Ensure that an authenticated user can delete an Irma Server."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email=TEST_MAIL, username=TEST_MAIL
        )
        self.client.force_authenticate(user=self.user)

        # Create an IrmaServer instance for testing
        self.irma_server = IrmaServer.objects.create(email=TEST_MAIL, version=VERSION)

    def test_delete_irma_server(self):
        url = reverse("portal_backend:irma-server-delete", args=[self.irma_server.id])

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(IrmaServer.objects.filter(id=self.irma_server.id).exists())

    def test_delete_irma_server_not_found(self):
        url = reverse("portal_backend:irma-server-delete", args=[9999])  # Non-existent ID

        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)
        
