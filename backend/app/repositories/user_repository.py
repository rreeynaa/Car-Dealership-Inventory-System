"""All database access for users lives here (Single Responsibility)."""

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import EmailAlreadyRegisteredError
from app.models import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, user: User) -> User:
        """Persist a user. The unique index makes duplicate detection race-safe."""
        self._db.add(user)
        try:
            self._db.commit()
        except IntegrityError as exc:
            self._db.rollback()
            raise EmailAlreadyRegisteredError(user.email) from exc
        self._db.refresh(user)
        return user

    def get_by_email(self, email: str) -> User | None:
        return self._db.scalar(select(User).where(User.email == email))

    def get_by_id(self, user_id: int) -> User | None:
        return self._db.get(User, user_id)