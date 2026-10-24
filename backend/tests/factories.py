"""Helpers for building test data."""

from app.core.security import create_access_token
from app.models import User


def auth_headers_for(user: User) -> dict[str, str]:
    """Authorization header carrying a valid JWT for the given user."""
    token = create_access_token(subject=str(user.id), role=user.role)
    return {"Authorization": f"Bearer {token}"}
