import pytest

URL = "/api/auth/register"
VALID = {"email": "jane@example.com", "password": "S3cure!pass"}


def test_register_creates_user(client):
    response = client.post(URL, json=VALID)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "jane@example.com"
    assert body["role"] == "user"
    assert isinstance(body["id"], int)


def test_register_never_returns_password_data(client):
    body = client.post(URL, json=VALID).json()

    assert "password" not in body
    assert "hashed_password" not in body


def test_register_ignores_client_supplied_role(client):
    """Privilege-escalation guard: clients cannot make themselves admin."""
    response = client.post(URL, json={**VALID, "role": "admin"})

    assert response.status_code == 201
    assert response.json()["role"] == "user"


def test_register_normalizes_email_to_lowercase(client):
    response = client.post(URL, json={**VALID, "email": "Jane@Example.COM"})

    assert response.json()["email"] == "jane@example.com"


def test_register_duplicate_email_returns_409(client):
    client.post(URL, json=VALID)

    assert client.post(URL, json=VALID).status_code == 409


def test_register_duplicate_email_is_case_insensitive(client):
    client.post(URL, json=VALID)

    response = client.post(URL, json={**VALID, "email": "JANE@example.com"})

    assert response.status_code == 409


@pytest.mark.parametrize(
    "password",
    ["Ab1", "onlyletters", "12345678"],
    ids=["too-short", "no-digit", "no-letter"],
)
def test_register_rejects_weak_password(client, password):
    response = client.post(URL, json={**VALID, "password": password})

    assert response.status_code == 422


def test_register_rejects_invalid_email(client):
    response = client.post(URL, json={**VALID, "email": "not-an-email"})

    assert response.status_code == 422


def test_register_rejects_password_over_bcrypt_limit(client):
    """bcrypt only uses the first 72 bytes, so longer inputs are refused."""
    response = client.post(URL, json={**VALID, "password": "a1" * 40})

    assert response.status_code == 422
