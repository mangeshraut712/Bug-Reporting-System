"""
Tests for accounts app.
"""
import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.db import IntegrityError, transaction
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import serializers, status

from accounts.serializers import validation_error_for_duplicate_user
from accounts.throttles import LoginRateThrottle, PasswordResetRateThrottle, RegisterRateThrottle

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
        response = api_client.post('/api/auth/register/', data)
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
        response = api_client.post('/api/auth/register/', data)
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
        assert response.data['access']
        assert response.data['refresh']
        assert 'key' not in response.data
        assert 'password' not in response.data['user']
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        me = api_client.get('/api/auth/users/me/')
        assert me.status_code == status.HTTP_200_OK
        assert me.data['email'] == user.email

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

    def test_registration_response_hides_password(self, api_client):
        """
        Registration confirms the new user and does not echo the password.
        """
        data = {
            'email': 'hidden@example.com',
            'username': 'hiddenuser',
            'first_name': 'Hidden',
            'last_name': 'User',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
        }
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['message'] == 'User registered successfully'
        assert response.data['user']['email'] == 'hidden@example.com'
        assert 'password' not in response.data['user']

    def test_duplicate_email_rejected(self, api_client, user):
        """
        A second account cannot reuse an email address.
        """
        data = {
            'email': user.email,
            'username': 'someoneelse',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
        }
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert User.objects.filter(email=user.email).count() == 1

    def test_short_password_rejected(self, api_client):
        """
        Passwords shorter than 8 characters are rejected.
        """
        data = {
            'email': 'short@example.com',
            'username': 'shortuser',
            'password': 'short',
            'password_confirm': 'short',
        }
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not User.objects.filter(email='short@example.com').exists()

    def test_current_user_from_viewset(self, authenticated_client):
        """
        The accounts viewset returns the signed-in user.
        """
        api_client, user = authenticated_client
        response = api_client.get('/api/auth/users/me/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email
        assert response.data['username'] == user.username
        assert 'password' not in response.data

    def test_current_user_requires_authentication(self, api_client):
        """
        Anonymous requests for the current user use the shared 401 shape.
        """
        response = api_client.get('/api/auth/users/me/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data['error'] == 'Unauthorized'

    def test_user_string_is_email(self, user):
        """
        The custom user displays its email.
        """
        assert str(user) == 'test@example.com'
        assert user.display_name() == 'Test User'

    def test_registration_ignores_staff_flags(self, api_client):
        """
        Clients cannot grant themselves staff or superuser during registration.
        """
        data = {
            'email': 'Staff@Example.com',
            'username': 'staffish',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
            'is_staff': True,
            'is_superuser': True,
        }
        response = api_client.post('/api/auth/register/', data)
        assert response.status_code == status.HTTP_201_CREATED
        created = User.objects.get(username='staffish')
        assert created.email == 'staff@example.com'
        assert created.is_staff is False
        assert created.is_superuser is False
        assert created.check_password('testpass123')

    def test_duplicate_email_is_case_insensitive(self, api_client, user):
        """
        Email uniqueness does not depend on letter case.
        """
        response = api_client.post('/api/auth/register/', {
            'email': user.email.upper(),
            'username': 'someoneelse',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert User.objects.filter(email__iexact=user.email).count() == 1

    def test_common_and_numeric_passwords_rejected(self, api_client):
        """
        Django's password validators reject common and all-numeric passwords.
        """
        cases = (
            ('common@example.com', 'commonuser', 'password'),
            ('numeric@example.com', 'numericuser', '12345678'),
        )
        for email, username, password in cases:
            response = api_client.post('/api/auth/register/', {
                'email': email,
                'username': username,
                'password': password,
                'password_confirm': password,
            })
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert not User.objects.filter(email=email).exists()

    def test_login_unknown_email_and_bad_password_match(self, api_client, user):
        """
        Unknown accounts and wrong passwords return the same failure.
        """
        unknown = api_client.post('/api/auth/login/', {
            'email': 'missing@example.com',
            'password': 'testpass123',
        })
        wrong = api_client.post('/api/auth/login/', {
            'email': user.email,
            'password': 'not-the-password',
        })
        assert unknown.status_code == status.HTTP_400_BAD_REQUEST
        assert wrong.status_code == status.HTTP_400_BAD_REQUEST
        assert unknown.data == wrong.data
        assert 'disabled' not in str(unknown.data).lower()

    def test_inactive_user_cannot_login(self, api_client, user):
        """
        Disabled accounts cannot obtain a token.
        """
        user.is_active = False
        user.save(update_fields=['is_active'])
        response = api_client.post('/api/auth/login/', {
            'email': user.email.upper(),
            'password': 'testpass123',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'access' not in response.data

    def test_login_does_not_set_session_cookie(self, api_client, user):
        """
        Login returns JWTs and does not plant a session cookie.
        """
        response = api_client.post('/api/auth/login/', {
            'email': user.email,
            'password': 'testpass123',
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'sessionid' not in response.cookies

    def test_logout_blacklists_refresh_token(self, api_client, user):
        """
        Logout revokes the refresh token so it cannot be rotated again.
        """
        login = api_client.post('/api/auth/login/', {
            'email': user.email,
            'password': 'testpass123',
        })
        refresh = login.data['refresh']
        logout = api_client.post('/api/auth/logout/', {'refresh': refresh})
        assert logout.status_code == status.HTTP_200_OK
        reused = api_client.post('/api/auth/token/refresh/', {'refresh': refresh})
        assert reused.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_rotates_and_old_token_stops_working(self, api_client, user):
        """
        A refresh token can be exchanged once, and the replacement is what remains valid.
        """
        login = api_client.post('/api/auth/login/', {
            'email': user.email,
            'password': 'testpass123',
        })
        first = api_client.post('/api/auth/token/refresh/', {'refresh': login.data['refresh']})
        assert first.status_code == status.HTTP_200_OK
        assert first.data['access']
        assert first.data['refresh']
        assert first.data['refresh'] != login.data['refresh']
        second = api_client.post('/api/auth/token/refresh/', {'refresh': login.data['refresh']})
        assert second.status_code == status.HTTP_401_UNAUTHORIZED
        third = api_client.post('/api/auth/token/refresh/', {'refresh': first.data['refresh']})
        assert third.status_code == status.HTTP_200_OK

    def test_user_directory_is_not_exposed(self, authenticated_client):
        """
        Authenticated clients cannot list every account.
        """
        api_client, _user = authenticated_client
        for path in ('/api/auth/users/', '/api/auth/register/users/'):
            response = api_client.get(path)
            assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_profile_update_cannot_change_email_or_staff(self, authenticated_client):
        """
        The signed-in user can edit their name but not their email or staff flag.
        """
        api_client, user = authenticated_client
        response = api_client.patch('/api/auth/user/', {
            'email': 'taken@example.com',
            'is_staff': True,
            'is_superuser': True,
            'first_name': 'Renamed',
        })
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.email == 'test@example.com'
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.first_name == 'Renamed'

    def test_login_is_throttled(self, api_client, monkeypatch):
        """
        Repeated login attempts from one client are rate limited.
        """
        monkeypatch.setattr(LoginRateThrottle, 'rate', '1/min', raising=False)
        cache.clear()
        payload = {'email': 'missing@example.com', 'password': 'testpass123'}
        first = api_client.post('/api/auth/login/', payload)
        second = api_client.post('/api/auth/login/', payload)
        assert first.status_code == status.HTTP_400_BAD_REQUEST
        assert second.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert second.data['error'] == 'Too Many Requests'

    def test_register_is_throttled(self, api_client, monkeypatch):
        """
        Repeated registration attempts from one client are rate limited.
        """
        monkeypatch.setattr(RegisterRateThrottle, 'rate', '1/min', raising=False)
        cache.clear()
        first = api_client.post('/api/auth/register/', {
            'email': 'one@example.com',
            'username': 'oneuser',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
        })
        second = api_client.post('/api/auth/register/', {
            'email': 'two@example.com',
            'username': 'twouser',
            'password': 'testpass123',
            'password_confirm': 'testpass123',
        })
        assert first.status_code == status.HTTP_201_CREATED
        assert second.status_code == status.HTTP_429_TOO_MANY_REQUESTS

    def test_duplicate_username_is_case_insensitive(self, api_client, user):
        """Usernames that differ only by letter case are rejected."""
        response = api_client.post('/api/auth/register/', {
            'email': 'other@example.com',
            'username': user.username.upper(),
            'password': 'testpass123',
            'password_confirm': 'testpass123',
        })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert User.objects.filter(username__iexact=user.username).count() == 1

    def test_database_rejects_case_variant_username_and_email(self, user):
        """The database, not only the serializer, treats identity as case-insensitive."""
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(
                    email='other@example.com',
                    username=user.username.upper(),
                    password='testpass123',
                )
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                User.objects.create_user(
                    email=user.email.upper(),
                    username='othername',
                    password='testpass123',
                )

    def test_duplicate_username_constraint_is_reported_as_username(self):
        """A username collision is not described as a duplicate email."""
        with pytest.raises(serializers.ValidationError) as caught:
            validation_error_for_duplicate_user(
                IntegrityError('UNIQUE constraint failed: accounts_user.username')
            )
        assert 'username' in caught.value.detail

    def test_profile_username_collision_is_case_insensitive(self, authenticated_client, another_user):
        """A profile update cannot take a username that differs only by case."""
        api_client, user = authenticated_client
        response = api_client.patch('/api/auth/user/', {'username': another_user.username.upper()})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        user.refresh_from_db()
        assert user.username == 'testuser'

    def test_profile_username_cannot_be_blank(self, authenticated_client):
        """A profile update cannot clear the username."""
        api_client, user = authenticated_client
        response = api_client.patch('/api/auth/user/', {'username': '   '})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        user.refresh_from_db()
        assert user.username == 'testuser'

    def test_password_change_requires_current_password_and_revokes_tokens(self, api_client, user):
        """Changing a password needs the current one and ends existing sessions."""
        login = api_client.post('/api/auth/login/', {
            'email': user.email,
            'password': 'testpass123',
        })
        assert login.status_code == status.HTTP_200_OK
        access = login.data['access']
        refresh = login.data['refresh']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')

        missing = api_client.post('/api/auth/password/change/', {
            'new_password1': 'replacement-pass-9',
            'new_password2': 'replacement-pass-9',
        })
        wrong = api_client.post('/api/auth/password/change/', {
            'old_password': 'not-the-password',
            'new_password1': 'replacement-pass-9',
            'new_password2': 'replacement-pass-9',
        })
        assert missing.status_code == status.HTTP_400_BAD_REQUEST
        assert wrong.status_code == status.HTTP_400_BAD_REQUEST
        user.refresh_from_db()
        assert user.check_password('testpass123')

        changed = api_client.post('/api/auth/password/change/', {
            'old_password': 'testpass123',
            'new_password1': 'replacement-pass-9',
            'new_password2': 'replacement-pass-9',
        })
        assert changed.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password('replacement-pass-9')

        assert api_client.get('/api/projects/').status_code == status.HTTP_401_UNAUTHORIZED
        recycled = api_client.post('/api/auth/token/refresh/', {'refresh': refresh})
        assert recycled.status_code == status.HTTP_401_UNAUTHORIZED

        api_client.credentials()
        relogin = api_client.post('/api/auth/login/', {
            'email': user.email,
            'password': 'replacement-pass-9',
        })
        assert relogin.status_code == status.HTTP_200_OK

    def test_password_reset_does_not_reveal_whether_the_account_exists(self, api_client, user):
        """Known and unknown addresses get the same reset response."""
        known = api_client.post('/api/auth/password/reset/', {'email': user.email})
        unknown = api_client.post('/api/auth/password/reset/', {'email': 'missing@example.com'})
        assert known.status_code == status.HTTP_200_OK
        assert unknown.status_code == status.HTTP_200_OK
        assert known.data == unknown.data

    def test_password_reset_accepts_a_stale_access_token(self, api_client, user):
        """A bad bearer token does not block an anonymous reset request."""
        api_client.credentials(HTTP_AUTHORIZATION='Bearer not-a-token')
        response = api_client.post('/api/auth/password/reset/', {'email': user.email})
        assert response.status_code == status.HTTP_200_OK

    def test_password_reset_is_throttled(self, api_client, monkeypatch):
        """Repeated reset requests from one client are rate limited."""
        monkeypatch.setattr(PasswordResetRateThrottle, 'rate', '1/min', raising=False)
        cache.clear()
        first = api_client.post('/api/auth/password/reset/', {'email': 'one@example.com'})
        second = api_client.post('/api/auth/password/reset/', {'email': 'two@example.com'})
        assert first.status_code == status.HTTP_200_OK
        assert second.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert second.data['error'] == 'Too Many Requests'

    def test_password_reset_confirm_changes_password_and_revokes_tokens(self, api_client, user):
        """A reset token sets a new password and ends sessions created before it."""
        login = api_client.post('/api/auth/login/', {
            'email': user.email,
            'password': 'testpass123',
        })
        access = login.data['access']
        refresh = login.data['refresh']
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        reset = api_client.post('/api/auth/password/reset/confirm/', {
            'uid': uid,
            'token': token,
            'new_password1': 'replacement-pass-9',
            'new_password2': 'replacement-pass-9',
        })
        assert reset.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.check_password('replacement-pass-9')
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access}')
        assert api_client.get('/api/projects/').status_code == status.HTTP_401_UNAUTHORIZED
        assert api_client.post('/api/auth/token/refresh/', {'refresh': refresh}).status_code == (
            status.HTTP_401_UNAUTHORIZED
        )
