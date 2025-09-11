from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

class RegisterTests(APITestCase):
    def test_register_success(self):
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
        url = reverse('register')
        data = {'username': 'testuser'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertIn('password', response.data)

    def test_register_duplicate_email(self):
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
