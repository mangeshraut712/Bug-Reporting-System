"""Edge cases for refresh-token revocation in accounts.models.User.save().

The happy path (a password change revokes tokens) is covered in
accounts/tests.py; these pin the gating and the blacklist deduplication.
"""
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import (
    BlacklistedToken,
    OutstandingToken,
)
from rest_framework_simplejwt.tokens import RefreshToken

pytestmark = pytest.mark.django_db

User = get_user_model()


def make_user():
    return User.objects.create_user(
        username='alice',
        email='alice@example.com',
        password='first-password-123',
    )


def is_blacklisted(user, refresh):
    outstanding = OutstandingToken.objects.get(user=user, jti=refresh['jti'])
    return BlacklistedToken.objects.filter(token=outstanding).exists()


def test_save_without_password_change_keeps_tokens():
    user = make_user()
    refresh = RefreshToken.for_user(user)

    user.first_name = 'Alice'
    user.save()

    assert not is_blacklisted(user, refresh)


def test_last_login_update_does_not_revoke_tokens():
    # UPDATE_LAST_LOGIN writes last_login with save(update_fields=['last_login'])
    # on every login; that save must not revoke the session it just issued.
    user = make_user()
    refresh = RefreshToken.for_user(user)

    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])

    assert not is_blacklisted(user, refresh)


def test_password_set_but_excluded_from_update_fields_is_not_revoked():
    user = make_user()
    refresh = RefreshToken.for_user(user)

    user.set_password('second-password-456')
    user.save(update_fields=['first_name'])

    assert not is_blacklisted(user, refresh)


def test_second_password_change_skips_already_blacklisted_tokens():
    # BlacklistedToken.token is one-to-one, so re-blacklisting the first
    # token on the second change would raise IntegrityError without dedup.
    user = make_user()
    first = RefreshToken.for_user(user)
    user.set_password('second-password-456')
    user.save(update_fields=['password'])

    second = RefreshToken.for_user(user)
    user.set_password('third-password-789')
    user.save(update_fields=['password'])

    assert is_blacklisted(user, first)
    assert is_blacklisted(user, second)
    assert BlacklistedToken.objects.count() == 2
