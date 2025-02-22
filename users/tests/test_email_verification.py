import os
import django
from django.test.utils import setup_test_environment

os.environ['DJANGO_SETTINGS_MODULE'] = 'ugogo.settings'
django.setup()
setup_test_environment()

from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from users.models import Users

class VerifyEmailViewTests(APITestCase):
    def setUp(self):
        self.user = Users.objects.create_user(
            email='test_2@example.com',
            password='password123',
            is_active=False,
            is_email_verified=False,
            email_verification_code='123456',
            code_expiration=timezone.now() + timezone.timedelta(hours=1)
        )
        self.url = reverse('verify-email')

    def test_verify_email_success(self):
        data = {
            'email': 'test_2@example.com',
            'email_verification_code': '123456'
        }
        response = self.client.post(self.url, data, format='json')
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(self.user.is_email_verified)
        self.assertTrue(self.user.is_active)

    def test_verify_email_missing_fields(self):
        data = {}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_verify_email_user_not_exist(self):
        data = {
            'email': 'nonexistent@example.com',
            'email_verification_code': '123456'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)

    def test_verify_email_invalid_code(self):
        data = {
            'email': 'test@example.com',
            'email_verification_code': 'wrongcode'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('error', response.data)

    def test_verify_email_code_expired(self):
        self.user.code_expiration = timezone.now() - timezone.timedelta(hours=1)
        self.user.save()
        data = {
            'email': 'test@example.com',
            'email_verification_code': '123456'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn('error', response.data)