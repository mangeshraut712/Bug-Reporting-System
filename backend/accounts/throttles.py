"""Rate limits for credential endpoints."""
from rest_framework.throttling import AnonRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """Slow repeated login attempts from one client."""

    scope = 'login'


class RegisterRateThrottle(AnonRateThrottle):
    """Slow repeated account creation from one client."""

    scope = 'register'


class RefreshRateThrottle(AnonRateThrottle):
    """Slow repeated refresh-token submissions from one client."""

    scope = 'refresh'
