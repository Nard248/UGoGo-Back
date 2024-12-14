from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import Users


class UserAuthTests(APITestCase):
    def setUp(self):
        # Register URL for user registration
        self.register_url = reverse("register")
        # Login URL for obtaining tokens
        self.login_url = reverse("token_obtain_pair")
        # Refresh token URL
        self.refresh_url = reverse("token_refresh")
        # Logout URL
        self.logout_url = reverse("token_blacklist")

        # Pre-created user data
        self.user_data = {
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "password123",
        }

        # Create a test user
        self.user = Users.objects.create_user(**self.user_data)

    def test_user_registration(self):
        """
        Test if a user can register successfully
        """
        new_user_data = {
            "email": "newuser@example.com",
            "first_name": "New",
            "last_name": "User",
            "password": "password123",
        }
        response = self.client.post(self.register_url, new_user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("user", response.data)
        self.assertIn("email", response.data["user"])
        self.assertEqual(response.data["user"]["email"], new_user_data["email"])

    def test_user_registration_invalid_email(self):
        """
        Test registration with an invalid email
        """
        invalid_user_data = {
            "email": "invalidemail",
            "first_name": "Invalid",
            "last_name": "User",
            "password": "password123",
        }
        response = self.client.post(self.register_url, invalid_user_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_user_login_success(self):
        """
        Test if a user can log in and obtain tokens
        """
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_user_login_invalid_credentials(self):
        """
        Test login with invalid credentials
        """
        login_data = {
            "email": self.user_data["email"],
            "password": "wrongpassword",
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_token_refresh(self):
        """
        Test if the refresh token generates a new access token
        """
        login_response = self.client.post(self.login_url, {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        })
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        refresh_token = login_response.data["refresh"]

        refresh_response = self.client.post(self.refresh_url, {"refresh": refresh_token})
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

    def test_user_logout(self):
        """
        Test if a user can log out and invalidate the refresh token
        """
        login_response = self.client.post(self.login_url, {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        })
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        refresh_token = login_response.data["refresh"]

        logout_response = self.client.post(self.logout_url, {"refresh": refresh_token})
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)

    def test_user_registration_missing_fields(self):
        """
        Test registration with missing required fields
        """
        missing_field_data = {
            "email": "",
            "first_name": "Missing",
            "last_name": "Fields",
            "password": "password123",
        }
        response = self.client.post(self.register_url, missing_field_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_user_login_non_existent_user(self):
        """
        Test login with non-existent user
        """
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123",
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", response.data)

    def test_token_refresh_invalid(self):
        """
        Test refreshing token with an invalid refresh token
        """
        refresh_response = self.client.post(self.refresh_url, {"refresh": "invalid_token"})
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("detail", refresh_response.data)
