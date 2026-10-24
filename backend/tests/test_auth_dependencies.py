from datetime import timedelta

import pytest
from fastapi import HTTPException

from app.api.deps import require_admin
from app.core.security import create_access_token
from app.models import Role, User
from tests.factories import auth_headers_for

ME = "/api/auth/me"


def test_me_returns_current_user(client, create_user):
    user = create_user("jane@example.com")

    response = client.get(ME, headers=auth_headers_for(user))

    assert response.status_code == 200
    assert response.json()["email"] == "jane@example.com"
    assert response.json()["id"] == user.id


def test_me_without_token_returns_401(client):
    response = client.get(ME)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_me_with_malformed_token_returns_401(client):
    response = client.get(ME, headers={"Authorization": "Bearer not-a-jwt"})

    assert response.status_code == 401


def test_me_with_expired_token_returns_401(client, create_user):
    user = create_user()
    token = create_access_token(str(user.id), user.role, expires_delta=timedelta(seconds=-1))

    response = client.get(ME, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_me_with_token_for_missing_user_returns_401(client):
    token = create_access_token("999999", Role.USER.value)

    response = client.get(ME, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401


def test_require_admin_allows_admin():
    admin = User(email="a@example.com", hashed_password="x", role=Role.ADMIN.value)

    assert require_admin(admin) is admin


def test_require_admin_rejects_regular_user():
    user = User(email="u@example.com", hashed_password="x", role=Role.USER.value)

    with pytest.raises(HTTPException) as exc_info:
        require_admin(user)

    assert exc_info.value.status_code == 403
