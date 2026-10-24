import pytest
from pydantic import ValidationError

from app.core.config import DEV_JWT_SECRET, Settings, normalize_database_url


def test_normalize_converts_heroku_style_scheme():
    url = "postgres://user:pw@host:5432/db"

    assert normalize_database_url(url) == "postgresql+psycopg://user:pw@host:5432/db"


def test_normalize_converts_plain_postgresql_scheme():
    url = "postgresql://user:pw@host:5432/db"

    assert normalize_database_url(url) == "postgresql+psycopg://user:pw@host:5432/db"


def test_normalize_leaves_explicit_driver_untouched():
    url = "postgresql+psycopg://user:pw@host:5432/db"

    assert normalize_database_url(url) == url


def test_settings_normalizes_database_url():
    settings = Settings(database_url="postgres://u:p@h:5432/d")

    assert settings.database_url.startswith("postgresql+psycopg://")


def test_cors_origins_are_split_and_trimmed():
    settings = Settings(cors_origins="https://a.example.com, https://b.example.com")

    assert settings.cors_origin_list == ["https://a.example.com", "https://b.example.com"]


def test_production_rejects_default_jwt_secret():
    with pytest.raises(ValidationError):
        Settings(environment="production", jwt_secret=DEV_JWT_SECRET)


def test_production_accepts_custom_jwt_secret():
    settings = Settings(environment="production", jwt_secret="x" * 40)

    assert settings.environment == "production"