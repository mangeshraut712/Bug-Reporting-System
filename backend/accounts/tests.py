"""
Tests for accounts app.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


@pytest.mark.django_db
class TestAuthEndpoints:
    """
    Test authentication endpoints.
    """

    def test_user_registration(self, api_client):
        """
        Test user registration.
        """
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
        }
        response = api_client.post('/api/auth/register/register/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email='newuser@example.com').exists()

    def test_user_registration_password_mismatch(self, api_client):
        """
        Test user registration with mismatched passwords.
        """
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'testpass123',
            'password_confirm': 'differentpass',
        }
        response = api_client.post('/api/auth/register/register/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_login(self, api_client, user):
        """
        Test user login.
        """
        data = {
            'email': 'test@example.com',
            'password': 'testpass123',
        }
        response = api_client.post('/api/auth/login/', data)
        assert response.status_code == status.HTTP_200_OK
        assert 'key' in response.data

    def test_user_login_invalid_credentials(self, api_client):
        """
        Test user login with invalid credentials.
        """
        data = {
            'email': 'nonexistent@example.com',
            'password': 'wrongpassword',
        }
        response = api_client.post('/api/auth/login/', data)
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_400_BAD_REQUEST]

    def test_get_current_user(self, authenticated_client):
        """
        Test getting current user information.
        """
        api_client, user = authenticated_client
        response = api_client.get('/api/auth/user/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('email') == user.email or response.data.get('id') == user.id
