"""Business rules for registration and login."""

from app.core.exceptions import InvalidCredentialsError
from app.core.security import create_access_token, hash_password, verify_password
from app.models import Role, User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate

# Verified against when the email is unknown, so response time does not reveal
# whether an account exists.
_DUMMY_HASH = hash_password("not-a-real-password-1")


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

    def login(self, email: str, password: str) -> tuple[User, str]:
        """Return the user and a JWT, or raise InvalidCredentialsError."""
        user = self._users.get_by_email(email)
        stored_hash = user.hashed_password if user else _DUMMY_HASH
        password_ok = verify_password(password, stored_hash)
        if user is None or not password_ok:
            raise InvalidCredentialsError
        token = create_access_token(subject=str(user.id), role=user.role)
        return user, token
