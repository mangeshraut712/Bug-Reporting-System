"""Shared request validation helpers."""
from collections.abc import Mapping

from rest_framework.exceptions import ValidationError

MAX_COMMENT_LENGTH = 5000
MAX_DESCRIPTION_LENGTH = 10_000
MAX_DATABASE_INTEGER = 2**63 - 1


def require_object_payload(data):
    """Return a mapping payload or reject JSON arrays and scalar values."""
    if not isinstance(data, Mapping):
        raise ValidationError({'non_field_errors': 'Expected a JSON object.'})
    return data


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
    if not 1 <= parsed <= MAX_DATABASE_INTEGER:
        raise ValidationError({field_name: 'Must be a positive integer.'})
    return parsed
