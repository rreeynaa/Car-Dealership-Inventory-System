from datetime import timedelta

import jwt
import pytest

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_password_does_not_store_plaintext():
    assert hash_password("S3cure!pass") != "S3cure!pass"


def test_hash_password_is_salted():
    assert hash_password("S3cure!pass") != hash_password("S3cure!pass")


def test_verify_password_accepts_correct_password():
    hashed = hash_password("S3cure!pass")

    assert verify_password("S3cure!pass", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("S3cure!pass")

    assert verify_password("wrong-password", hashed) is False


def test_access_token_round_trip_preserves_claims():
    token = create_access_token(subject="42", role="admin")

    claims = decode_access_token(token)

    assert claims["sub"] == "42"
    assert claims["role"] == "admin"


def test_expired_token_is_rejected():
    token = create_access_token(subject="42", role="user", expires_delta=timedelta(seconds=-1))

    with pytest.raises(jwt.ExpiredSignatureError):
        decode_access_token(token)


def test_tampered_token_is_rejected():
    token = create_access_token(subject="42", role="user")

    with pytest.raises(jwt.InvalidTokenError):
        decode_access_token(token + "x")
