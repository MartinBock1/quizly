from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

class RegisterTests(APITestCase):
    """
    Test suite for the user registration API endpoint.
    Covers successful registration, missing fields, and duplicate email cases.
    """
    def test_register_success(self):
        """
        Test: Successful user registration with valid data.
        Expects 201 Created and user exists in database.
        """
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'TestPassword123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('detail', response.data)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_register_missing_fields(self):
        """
        Test: Registration attempt with missing required fields.
        Expects 400 Bad Request and error details for missing fields.
        """
        url = reverse('register')
        data = {'username': 'testuser'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('password', response.data)

    def test_register_duplicate_email(self):
        """
        Test: Registration attempt with an email that already exists.
        Expects 400 Bad Request and error detail for email field.
        """
        User.objects.create_user(username='existing', email='test@example.com', password='pass')
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'test@example.com',
            'password': 'TestPassword123'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
