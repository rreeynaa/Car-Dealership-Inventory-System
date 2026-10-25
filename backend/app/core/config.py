"""Application settings, loaded from environment variables (and .env locally)."""

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEV_JWT_SECRET = "dev-only-secret-change-me-in-production-0123456789"


def normalize_database_url(url: str) -> str:
    """Make host-provided URLs work with the psycopg v3 driver.

    Hosting providers often supply postgres:// or postgresql://, which SQLAlchemy
    would map to the legacy psycopg2 driver.
    """
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


class Settings(BaseSettings):
    environment: str = "development"
    database_url: str = "postgresql+psycopg://dealership:dealership@localhost:5432/dealership"
    test_database_url: str = (
        "postgresql+psycopg://dealership:dealership@localhost:5432/dealership_test"
    )
    jwt_secret: str = DEV_JWT_SECRET
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    # Comma-separated list of allowed browser origins (the frontend URLs).
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # Rate limiting. Limits use slowapi syntax, e.g. "10/minute".
    rate_limit_enabled: bool = True
    login_rate_limit: str = "10/minute"
    register_rate_limit: str = "20/hour"
    purchase_rate_limit: str = "30/minute"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("database_url", "test_database_url")
    @classmethod
    def _normalize_urls(cls, value: str) -> str:
        return normalize_database_url(value)

    @model_validator(mode="after")
    def _forbid_dev_secret_in_production(self) -> "Settings":
        if self.environment == "production" and self.jwt_secret == DEV_JWT_SECRET:
            raise ValueError("JWT_SECRET must be set to a unique value in production")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
