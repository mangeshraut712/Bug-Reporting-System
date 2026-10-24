"""Shared request validation helpers."""
from rest_framework.exceptions import ValidationError

MAX_COMMENT_LENGTH = 5000
MAX_DESCRIPTION_LENGTH = 10_000


def parse_positive_int(value, field_name):
    """Return a positive integer, or None when the value was omitted.

    Invalid values raise a DRF ValidationError so callers respond with 400
    instead of letting the ORM raise ValueError.
    """
    if value is None or value == '':
        return None
    if isinstance(value, bool):
        raise ValidationError({field_name: 'Must be a positive integer.'})
    try:
        parsed = int(str(value))
    except (TypeError, ValueError):
        raise ValidationError({field_name: 'Must be a positive integer.'}) from None
    if parsed < 1:
        raise ValidationError({field_name: 'Must be a positive integer.'})
    return parsed
