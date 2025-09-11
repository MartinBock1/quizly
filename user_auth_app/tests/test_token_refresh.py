from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class TokenRefreshTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='refreshuser',
            email='refreshuser@example.com',
            password='refreshpass123'
        )
        self.login_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')

    def test_refresh_token_success(self):
        # Login to get tokens
        response = self.client.post(self.login_url, {
            'username': 'refreshuser',
            'password': 'refreshpass123'
        })
        self.assertEqual(response.status_code, 200)
        refresh_token = response.cookies.get('refresh_token').value
        # Set refresh_token as cookie for refresh request
        self.client.cookies['refresh_token'] = refresh_token
        refresh_response = self.client.post(self.refresh_url)
        self.assertEqual(refresh_response.status_code, 200)
        self.assertIn('access_token', refresh_response.cookies)
        self.assertEqual(refresh_response.data['detail'], 'Token refreshed')
        self.assertIn('access', refresh_response.data)

    def test_refresh_token_missing(self):
        # No refresh_token cookie set
        response = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], 'Refresh token not found!')

    def test_refresh_token_invalid(self):
        # Set an invalid refresh_token cookie
        self.client.cookies['refresh_token'] = 'invalidtoken'
        response = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Refresh token invalid!')
