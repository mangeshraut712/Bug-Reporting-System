"""
Guard against model changes that are missing from committed migrations.
"""
import pytest
from django.core.management import call_command


@pytest.mark.django_db
def test_models_have_no_pending_migrations():
    """``makemigrations --check`` exits non-zero when model state drifts from the migrations."""
    call_command('makemigrations', check=True, dry_run=True, verbosity=1)
