"""
User model for accounts app.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.db.models.functions import Lower


def blacklist_outstanding_tokens(user):
    """Revoke refresh tokens issued before a password change.

    Imported lazily because the blacklist models load AUTH_USER_MODEL.
    """
    from rest_framework_simplejwt.token_blacklist.models import (
        BlacklistedToken,
        OutstandingToken,
    )

    token_ids = list(OutstandingToken.objects.filter(user=user).values_list('pk', flat=True))
    if not token_ids:
        return
    already = set(
        BlacklistedToken.objects.filter(token_id__in=token_ids).values_list('token_id', flat=True)
    )
    BlacklistedToken.objects.bulk_create(
        [BlacklistedToken(token_id=token_id) for token_id in token_ids if token_id not in already]
    )


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    """
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(Lower('email'), name='accounts_user_email_ci_uniq'),
            models.UniqueConstraint(Lower('username'), name='accounts_user_username_ci_uniq'),
        ]

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        """Store emails canonically and revoke sessions when the password changes."""
        update_fields = kwargs.get('update_fields')
        if self.email and (update_fields is None or 'email' in update_fields):
            self.email = self.email.strip().lower()
        password_changed = False
        if self.pk and (update_fields is None or 'password' in update_fields):
            previous = type(self).objects.filter(pk=self.pk).values_list('password', flat=True).first()
            password_changed = previous is not None and previous != self.password
        if password_changed:
            with transaction.atomic():
                super().save(*args, **kwargs)
                blacklist_outstanding_tokens(self)
            return
        super().save(*args, **kwargs)

    def display_name(self):
        """Name shown in the API, falling back when the profile name is blank."""
        full_name = (self.get_full_name() or '').strip()
        return full_name or self.username or self.email


def user_display_name(user):
    """Return a display name, or None when the related user was deleted."""
    if user is None:
        return None
    return user.display_name()
