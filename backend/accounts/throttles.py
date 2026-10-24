"""Rate limits for credential endpoints."""
from rest_framework.throttling import AnonRateThrottle, SimpleRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """Slow repeated login attempts from one client."""

    scope = 'login'


class RegisterRateThrottle(AnonRateThrottle):
    """Slow repeated account creation from one client."""

    scope = 'register'


class RefreshRateThrottle(AnonRateThrottle):
    """Slow repeated refresh-token submissions from one client."""

    scope = 'refresh'


class PasswordResetRateThrottle(SimpleRateThrottle):
    """Slow password-reset attempts from one client, with or without a token."""

    scope = 'password_reset'

    def get_cache_key(self, request, view):
        return self.cache_format % {'scope': self.scope, 'ident': self.get_ident(request)}
