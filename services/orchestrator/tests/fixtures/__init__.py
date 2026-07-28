"""Shared test fixtures for EP-005 privacy / ignore acceptance (T004)."""

from tests.fixtures.ignore_exclusion_repo import (
    ALLOWED_REL_PATHS,
    EXCLUDED_REL_PATHS,
    materialize_ignore_exclusion_repo,
)

__all__ = [
    "ALLOWED_REL_PATHS",
    "EXCLUDED_REL_PATHS",
    "materialize_ignore_exclusion_repo",
]
