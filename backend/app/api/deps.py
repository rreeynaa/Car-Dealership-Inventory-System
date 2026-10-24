"""Reusable FastAPI dependencies: authentication and role checks."""

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models import Role, User
from app.repositories.user_repository import UserRepository

# auto_error=False so we answer 401 ourselves (older FastAPI returned 403).
# This also adds the "Authorize" button to Swagger UI.
bearer_scheme = HTTPBearer(
    auto_error=False,
    description="Paste the access_token returned by POST /api/auth/login",
)


def _unauthorized() -> HTTPException:
    return HTTPException(
        status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Resolve the bearer token to a user, or raise 401.

    The role is read from the database, not the token, so role changes
    take effect immediately.
    """
    if credentials is None:
        raise _unauthorized()
    try:
        claims = decode_access_token(credentials.credentials)
        user_id = int(claims["sub"])
    except (jwt.InvalidTokenError, KeyError, ValueError):
        raise _unauthorized() from None
    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise _unauthorized()
    return user


def require_admin(user: Annotated[User, Depends(get_current_user)]) -> User:
    """Allow only admins, otherwise raise 403."""
    if user.role != Role.ADMIN.value:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
    return user
