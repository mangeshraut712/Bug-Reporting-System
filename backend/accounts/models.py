"""
User model for accounts app.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    """
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.email

    def display_name(self):
        """Name shown in the API, falling back when the profile name is blank."""
        full_name = (self.get_full_name() or '').strip()
        return full_name or self.username or self.email


def user_display_name(user):
    """Return a display name, or None when the related user was deleted."""
    if user is None:
        return None
    return user.display_name()
