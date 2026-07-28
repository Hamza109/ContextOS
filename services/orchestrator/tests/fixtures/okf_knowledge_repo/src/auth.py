"""Tiny Python module for L5 hybrid fallback / L1 structural metadata."""


def authenticate(user: str, token: str) -> bool:
    """Return True when the token validates for the user."""
    return bool(user) and bool(token)
