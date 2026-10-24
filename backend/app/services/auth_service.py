"""Business rules for registration and login."""

from app.core.security import hash_password
from app.models import Role, User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class AuthService:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    def register(self, data: UserCreate) -> User:
        """Create a regular user. Admins are never created through this path."""
        user = User(
            email=data.email,
            hashed_password=hash_password(data.password),
            role=Role.USER.value,
        )
        return self._users.add(user)
