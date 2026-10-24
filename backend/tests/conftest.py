import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Role, User
from tests.factories import auth_headers_for


@pytest.fixture(scope="session")
def engine():
    """Create a clean schema in the dedicated test database once per run."""
    engine = create_engine(settings.test_database_url)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_session(engine):
    """A session wrapped in an outer transaction that is rolled back after each test.

    create_savepoint lets code under test call session.commit()/rollback()
    without ending the outer transaction.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db_session):
    """TestClient whose requests use the rolled-back test session."""

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def create_user(db_session):
    """Factory fixture: persist a user directly (tokens are minted in tests, no login)."""

    def _create(email: str = "user@example.com", role: str = Role.USER.value) -> User:
        user = User(email=email, hashed_password="not-a-real-hash", role=role)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create


@pytest.fixture
def user_headers(create_user):
    return auth_headers_for(create_user("user@example.com", Role.USER.value))


@pytest.fixture
def admin_headers(create_user):
    return auth_headers_for(create_user("admin@example.com", Role.ADMIN.value))
