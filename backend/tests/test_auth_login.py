from app.core.security import decode_access_token

REGISTER = "/api/auth/register"
LOGIN = "/api/auth/login"
CREDS = {"email": "jane@example.com", "password": "S3cure!pass"}


def register_jane(client) -> dict:
    return client.post(REGISTER, json=CREDS).json()


def test_login_returns_bearer_token_and_user(client):
    register_jane(client)

    response = client.post(LOGIN, json=CREDS)

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["email"] == "jane@example.com"
    assert body["user"]["role"] == "user"


def test_login_token_carries_user_id_and_role(client):
    user = register_jane(client)

    token = client.post(LOGIN, json=CREDS).json()["access_token"]

    claims = decode_access_token(token)
    assert claims["sub"] == str(user["id"])
    assert claims["role"] == "user"


def test_login_email_is_case_insensitive(client):
    register_jane(client)

    response = client.post(LOGIN, json={**CREDS, "email": "JANE@Example.com"})

    assert response.status_code == 200


def test_login_wrong_password_returns_401(client):
    register_jane(client)

    response = client.post(LOGIN, json={**CREDS, "password": "Wrong!pass1"})

    assert response.status_code == 401


def test_login_unknown_user_gets_same_error_as_wrong_password(client):
    """Identical responses prevent attackers from discovering which emails exist."""
    register_jane(client)
    wrong_password = client.post(LOGIN, json={**CREDS, "password": "Wrong!pass1"})

    unknown_user = client.post(LOGIN, json={"email": "nobody@example.com", "password": "x1y2z3w4"})

    assert unknown_user.status_code == 401
    assert unknown_user.json() == wrong_password.json()


def test_login_missing_fields_returns_422(client):
    assert client.post(LOGIN, json={"email": "jane@example.com"}).status_code == 422