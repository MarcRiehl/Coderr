from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from profiles_app.models import Profile

User = get_user_model()


class RegistrationTests(APITestCase):

    registration_url = "/api/registration/"

    def setUp(self):

        self.data = {
            "username": "testuser",
            "email": "user@localhost.de",
            "password": "examplePassword",
            "repeated_password": "examplePassword",
            "type": "customer",
        }

    def test_registration_successful(self):
        """Valid data creates the user, profile and token and returns 201."""
        response = self.client.post(
            self.registration_url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(User.objects.filter(username="testuser").exists())

        user = User.objects.get(username="testuser")

        self.assertTrue(user.check_password("examplePassword"))

        self.assertIn("token", response.data)

        self.assertEqual(response.data["username"], "testuser")

        self.assertEqual(response.data["email"], "user@localhost.de")

        self.assertIn("user_id", response.data)

        self.assertTrue(Profile.objects.filter(

            user_id=response.data["user_id"]).exists())

    def test_registration_passwords_do_not_match(self):
        """Mismatched passwords return 400."""

        self.data["repeated_password"] = "differentPassword"

        response = self.client.post(
            self.registration_url, self.data, format="json",)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_duplicate_username(self):
        """An already existing username returns 400."""
        User.objects.create_user(
            username="testuser", email="existing@mail.de", password="examplePassword")

        response = self.client.post(
            self.registration_url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_missing_username(self):
        """A missing username returns 400."""
        self.data.pop("username")

        response = self.client.post(
            self.registration_url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_invalid_email(self):
        """An invalid email format returns 400."""
        self.data["email"] = "invalid-email"

        response = self.client.post(
            self.registration_url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class LoginTests(APITestCase):
    login_url = "/api/login/"

    def setUp(self):
        self.username = "testuser"
        self.password = "examplePassword"

        User.objects.create_user(
            username=self.username, email="user@localhost.de", password=self.password, type="customer")

        self.data = {
            "username": self.username,
            "password": self.password,
        }

    def test_login_successful(self):
        """Valid credentials return 200."""
        response = self.client.post(self.login_url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_wrong_password(self):
        """A wrong password returns 400."""
        self.data["password"] = "wrongPassword"

        response = self.client.post(self.login_url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_unknown_username(self):
        """An unknown username returns 400."""
        self.data["username"] = "testUser123"

        response = self.client.post(self.login_url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_password(self):
        """A missing password returns 400."""
        self.data.pop("password")

        response = self.client.post(self.login_url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_username(self):
        """A missing username returns 400."""
        self.data.pop("username")

        response = self.client.post(self.login_url, self.data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
