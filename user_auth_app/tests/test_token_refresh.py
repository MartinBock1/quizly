from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model


class TokenRefreshTests(APITestCase):
    """
    Test suite for the token refresh API endpoint.
    Covers successful refresh, missing token, and invalid token cases.
    """
    def setUp(self):
        """
        Set up a test user and URLs for login and token refresh.
        """
        self.user = get_user_model().objects.create_user(
            username='refreshuser',
            email='refreshuser@example.com',
            password='refreshpass123'
        )
        self.login_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')

    def test_refresh_token_success(self):
        """
        Test: Successfully refreshes access token using a valid refresh token cookie.
        Expects new access token in cookies and response data.
        """
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
        """
        Test: Attempt to refresh token without providing a refresh token cookie.
        Expects 400 Bad Request and error detail in response.
        """
        # No refresh_token cookie set
        response = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], 'Refresh token not found!')

    def test_refresh_token_invalid(self):
        """
        Test: Attempt to refresh token with an invalid refresh token cookie.
        Expects 401 Unauthorized and error detail in response.
        """
        # Set an invalid refresh_token cookie
        self.client.cookies['refresh_token'] = 'invalidtoken'
        response = self.client.post(self.refresh_url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['detail'], 'Refresh token invalid!')
