import pytest
from app.core.limiter import limiter

from app.core.config import settings
from tests.factories import make_vehicle


@pytest.fixture
def rate_limiting(monkeypatch):
    """Turn the limiter on for one test (it is off for the rest of the suite)."""
    limiter.reset()
    monkeypatch.setattr(limiter, "enabled", True)
    yield
    limiter.reset()


def test_login_is_rate_limited(client, rate_limiting, monkeypatch):
    monkeypatch.setattr(settings, "login_rate_limit", "3/minute")
    credentials = {"email": "nobody@example.com", "password": "Wrong!pass1"}

    codes = [client.post("/api/auth/login", json=credentials).status_code for _ in range(4)]

    assert codes == [401, 401, 401, 429]


def test_register_is_rate_limited(client, rate_limiting, monkeypatch):
    monkeypatch.setattr(settings, "register_rate_limit", "2/minute")

    codes = [
        client.post(
            "/api/auth/register", json={"email": f"user{i}@example.com", "password": "S3cure!pass"}
        ).status_code
        for i in range(3)
    ]

    assert codes == [201, 201, 429]


def test_purchase_is_rate_limited(client, user_headers, db_session, rate_limiting, monkeypatch):
    monkeypatch.setattr(settings, "purchase_rate_limit", "2/minute")
    vehicle = make_vehicle(quantity=10)
    db_session.add(vehicle)
    db_session.commit()

    codes = [
        client.post(f"/api/vehicles/{vehicle.id}/purchase", headers=user_headers).status_code
        for _ in range(3)
    ]

    assert codes == [200, 200, 429]
