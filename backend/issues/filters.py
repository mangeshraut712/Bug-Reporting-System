"""Query filters for issue lists."""
from django.db.models import Q
from rest_framework.exceptions import ValidationError

from .models import Issue

MAX_SEARCH_LENGTH = 200


def filter_issues(queryset, params):
    """Filter by status, priority, and search text.

    Search uses a single Q expression so a status or priority filter already
    applied to ``queryset`` stays in effect, and a row that matches both the
    title and the description is returned once.
    """
    status = params.get('status') or ''
    priority = params.get('priority') or ''
    search = params.get('search') or ''

    if status:
        valid_status = {choice for choice, _label in Issue.STATUS_CHOICES}
        if status not in valid_status:
            raise ValidationError({'status': 'Invalid status.'})
        queryset = queryset.filter(status=status)

    if priority:
        valid_priority = {choice for choice, _label in Issue.PRIORITY_CHOICES}
        if priority not in valid_priority:
            raise ValidationError({'priority': 'Invalid priority.'})
        queryset = queryset.filter(priority=priority)

    if search:
        if len(search) > MAX_SEARCH_LENGTH:
            raise ValidationError({'search': 'Search text is too long.'})
        term = search.strip()
        if term:
            queryset = queryset.filter(
                Q(title__icontains=term) | Q(description__icontains=term)
            )
    return queryset
