"""
Pytest configuration and fixtures.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

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
def another_user(db):
    """
    Fixture to create another test user.
    """
    return User.objects.create_user(
        email='another@example.com',
        username='anotheruser',
        password='testpass123',
        first_name='Another',
        last_name='User'
    )


@pytest.fixture
def authenticated_client(api_client, user):
    """
    Fixture to provide an authenticated API client.
    """
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client, user


@pytest.fixture
def authenticated_client_other(api_client, another_user):
    """
    Fixture to provide an authenticated API client for another user.
    """
    refresh = RefreshToken.for_user(another_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client, another_user


@pytest.fixture
def project(db, user):
    """
    Fixture to create a test project.
    """
    from projects.models import Project
    return Project.objects.create(
        name='Test Project',
        description='A test project for testing',
        created_by=user
    )


@pytest.fixture
def issue(db, project, user, another_user):
    """
    Fixture to create a test issue.
    """
    from issues.models import Issue
    return Issue.objects.create(
        title='Test Issue',
        description='A test issue for testing',
        status='open',
        priority='medium',
        project=project,
        reporter=user,
        assignee=another_user
    )


@pytest.fixture
def comment(db, issue, user):
    """
    Fixture to create a test comment.
    """
    from comments.models import Comment
    return Comment.objects.create(
        content='Test comment',
        issue=issue,
        author=user
    )
