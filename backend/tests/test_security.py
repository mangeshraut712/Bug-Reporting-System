"""Regression tests for configuration and cross-cutting security controls."""
import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.test import Client
from rest_framework import status

from bug_tracking.exception_handler import custom_exception_handler
from bug_tracking.security import (
    parse_allowed_hosts,
    parse_origins,
    production_security_settings,
    resolve_secret_key,
)


def test_placeholder_secret_rejected_when_debug_disabled():
    """A known development key cannot sign production tokens."""
    with pytest.raises(ImproperlyConfigured):
        resolve_secret_key('django-insecure-dev-key-change-in-production', debug=False)


def test_short_secret_rejected_when_debug_disabled():
    """Production keys must be long enough to be unguessable."""
    with pytest.raises(ImproperlyConfigured):
        resolve_secret_key('x' * 49, debug=False)


def test_debug_allows_missing_secret():
    """Local debug can boot without a configured secret."""
    assert resolve_secret_key('', debug=True).startswith('django-insecure-')


def test_production_secret_accepted():
    """A long unique key is kept as the signing key."""
    key = 'a' * 50
    assert resolve_secret_key(key, debug=False) == key


def test_wildcard_hosts_rejected_when_debug_disabled():
    """Production must name the hosts it serves."""
    with pytest.raises(ImproperlyConfigured):
        parse_allowed_hosts('*', debug=False)


def test_wildcard_origin_rejected():
    """CORS cannot be opened to every origin."""
    with pytest.raises(ImproperlyConfigured):
        parse_origins('https://app.example, *')


def test_production_security_flags():
    """The production profile sets HSTS, secure cookies, and frame denial."""
    flags = production_security_settings()
    assert flags['SECURE_SSL_REDIRECT'] is True
    assert flags['SECURE_HSTS_SECONDS'] >= 31_536_000
    assert flags['SESSION_COOKIE_SECURE'] is True
    assert flags['CSRF_COOKIE_SECURE'] is True
    assert flags['CSRF_COOKIE_HTTPONLY'] is True
    assert flags['X_FRAME_OPTIONS'] == 'DENY'


def test_runtime_auth_configuration():
    """The API authenticates with JWTs and does not start a session at login."""
    assert settings.REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] == (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
    assert settings.REST_AUTH['USE_JWT'] is True
    assert settings.REST_AUTH['SESSION_LOGIN'] is False
    assert settings.REST_AUTH['JWT_AUTH_COOKIE'] is None
    assert settings.REST_AUTH['JWT_AUTH_REFRESH_COOKIE'] is None
    assert settings.CORS_ALLOW_CREDENTIALS is False
    assert 'rest_framework_simplejwt.token_blacklist' in settings.INSTALLED_APPS
    assert settings.SESSION_COOKIE_SECURE is False


def test_unhandled_exception_hides_internal_detail():
    """Unexpected failures return a generic JSON body."""
    response = custom_exception_handler(RuntimeError('db password=super-secret'), None)
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.data['error'] == 'Server Error'
    assert 'super-secret' not in str(response.data)


@pytest.mark.django_db
def test_session_cookie_does_not_authorize_api(user):
    """A Django session, including one from the admin, does not authorize the API."""
    client = Client()
    client.force_login(user)
    response = client.get('/api/projects/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()['error'] == 'Unauthorized'


@pytest.mark.django_db
def test_admin_post_without_csrf_token_is_rejected():
    """The admin login form still requires a CSRF token."""
    client = Client(enforce_csrf_checks=True)
    response = client.post('/admin/login/', {'username': 'admin', 'password': 'admin'})
    assert response.status_code == status.HTTP_403_FORBIDDEN
