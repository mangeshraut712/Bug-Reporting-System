"""Production secret and browser-security settings."""
from django.core.exceptions import ImproperlyConfigured

# Used only when DEBUG is on and no SECRET_KEY was provided.
DEV_SECRET_KEY = 'django-insecure-dev-key-change-in-production'  # noqa: S105

INSECURE_SECRET_KEYS = frozenset({
    '',
    'changeme',
    'change-me',
    'secret',
    'your-secret-key-here-change-in-production',
    'your-secret-key-change-in-production',
    DEV_SECRET_KEY,
})

MIN_SECRET_LENGTH = 50


def resolve_secret_key(secret_key, *, debug):
    """Return a signing key, refusing known placeholders when DEBUG is off."""
    cleaned = (secret_key or '').strip()
    if debug:
        return cleaned or DEV_SECRET_KEY
    if cleaned.lower() in INSECURE_SECRET_KEYS or len(cleaned) < MIN_SECRET_LENGTH:
        raise ImproperlyConfigured(
            'Set SECRET_KEY to a unique value of at least '
            f'{MIN_SECRET_LENGTH} characters when DEBUG is False.'
        )
    return cleaned


def parse_csv(raw):
    """Split a comma-separated setting and drop blank items."""
    return [item.strip() for item in (raw or '').split(',') if item.strip()]


def parse_allowed_hosts(raw, *, debug):
    """Require an explicit host list outside local debug."""
    hosts = parse_csv(raw)
    if not debug and (not hosts or '*' in hosts):
        raise ImproperlyConfigured('Set explicit ALLOWED_HOSTS when DEBUG is False.')
    return hosts


def parse_origins(raw):
    """Parse CORS/CSRF origins and reject a wildcard origin."""
    origins = parse_csv(raw)
    if '*' in origins:
        raise ImproperlyConfigured('Origins cannot contain "*".')
    return origins


def production_security_settings():
    """Cookie, HSTS, and redirect flags for a TLS deployment."""
    return {
        'SECURE_SSL_REDIRECT': True,
        'SECURE_HSTS_SECONDS': 31_536_000,
        'SECURE_HSTS_INCLUDE_SUBDOMAINS': True,
        'SECURE_HSTS_PRELOAD': True,
        'SECURE_PROXY_SSL_HEADER': ('HTTP_X_FORWARDED_PROTO', 'https'),
        'SECURE_CONTENT_TYPE_NOSNIFF': True,
        'SECURE_REFERRER_POLICY': 'same-origin',
        'SESSION_COOKIE_SECURE': True,
        'SESSION_COOKIE_HTTPONLY': True,
        'SESSION_COOKIE_SAMESITE': 'Lax',
        'CSRF_COOKIE_SECURE': True,
        'CSRF_COOKIE_HTTPONLY': True,
        'CSRF_COOKIE_SAMESITE': 'Lax',
        'X_FRAME_OPTIONS': 'DENY',
    }
