"""
Pytest configuration and fixtures.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework.throttling import SimpleRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


@pytest.fixture(autouse=True)
def relaxed_auth_throttles():
    """Keep credential throttles from tripping the rest of the suite.

    DRF copies throttle rates onto the throttle class at import, so the suite
    updates that mapping in place instead of replacing the settings dict.
    """
    rates = SimpleRateThrottle.THROTTLE_RATES
    saved = dict(rates)
    rates.update({
        'login': '1000/min',
        'register': '1000/min',
        'refresh': '1000/min',
    })
    yield
    rates.clear()
    rates.update(saved)


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


def _client_for(user):
    """Build a client that does not share credentials with another fixture."""
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return client, user


@pytest.fixture
def authenticated_client(user):
    """
    Fixture to provide an authenticated API client.
    """
    return _client_for(user)


@pytest.fixture
def authenticated_client_other(another_user):
    """
    Fixture to provide an authenticated API client for another user.
    """
    return _client_for(another_user)


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
