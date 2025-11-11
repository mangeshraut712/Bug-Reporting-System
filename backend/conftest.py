"""
Pytest configuration and fixtures.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.fixture
def api_client():
    """
    Fixture to provide an API client.
    """
    return APIClient()


@pytest.fixture
def user(db):
    """
    Fixture to create a test user.
    """
    return User.objects.create_user(
        email='test@example.com',
        username='testuser',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """
    Fixture to provide an authenticated API client.
    """
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client, user
