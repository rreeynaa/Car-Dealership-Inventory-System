import pytest

from app.core.exceptions import EmailAlreadyRegisteredError
from app.models import Role, User
from app.repositories.user_repository import UserRepository


def make_user(email: str = "jane@example.com") -> User:
    return User(email=email, hashed_password="hashed")


def test_add_persists_user_with_generated_id(db_session):
    repo = UserRepository(db_session)

    saved = repo.add(make_user())

    assert saved.id is not None


def test_new_user_defaults_to_user_role(db_session):
    repo = UserRepository(db_session)

    saved = repo.add(make_user())

    assert saved.role == Role.USER.value


def test_get_by_email_returns_matching_user(db_session):
    repo = UserRepository(db_session)
    repo.add(make_user("jane@example.com"))

    found = repo.get_by_email("jane@example.com")

    assert found is not None
    assert found.email == "jane@example.com"


def test_get_by_email_returns_none_when_missing(db_session):
    repo = UserRepository(db_session)

    assert repo.get_by_email("nobody@example.com") is None


def test_add_duplicate_email_raises(db_session):
    repo = UserRepository(db_session)
    repo.add(make_user("jane@example.com"))

    with pytest.raises(EmailAlreadyRegisteredError):
        repo.add(make_user("jane@example.com"))
