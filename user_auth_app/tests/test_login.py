from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

class LoginTests(APITestCase):
    """
    Test suite for the login API endpoint.
    Covers successful login, invalid credentials, and missing fields.
    """
    def setUp(self):
        """
        Set up a test user for authentication tests.
        """
        self.user = User.objects.create_user(username='testuser', email='testuser@example.com', password='TestPassword123')

    def test_login_success(self):
        """
        Test: Successful login with valid credentials.
        Expects user details and success message in response.
        """
        url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'TestPassword123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')

    def test_login_invalid_credentials(self):
        """
        Test: Login attempt with invalid password.
        Expects 401 Unauthorized and error detail in response.
        """
        url = reverse('token_obtain_pair')
        data = {
            'username': 'testuser',
            'password': 'WrongPassword'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

    def test_login_missing_fields(self):
        """
        Test: Login attempt with missing password field.
        Expects 401 Unauthorized in response.
        """
        url = reverse('token_obtain_pair')
        data = {'username': 'testuser'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
