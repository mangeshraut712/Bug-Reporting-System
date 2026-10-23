"""View helpers shared by the API."""
from bug_tracking.validation import parse_positive_int


class PositiveIntLookupMixin:
    """Reject non-numeric detail lookups before they reach the database."""

    def get_object(self):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        parse_positive_int(self.kwargs.get(lookup_url_kwarg), lookup_url_kwarg)
        return super().get_object()
