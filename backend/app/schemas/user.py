from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

BCRYPT_MAX_BYTES = 72


class UserCreate(BaseModel):
    # Extra fields such as "role" are ignored, never stored.
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("email")
    @classmethod
    def _lowercase_email(cls, value: str) -> str:
        return value.lower()

    @field_validator("password")
    @classmethod
    def _check_password_strength(cls, value: str) -> str:
        if len(value.encode("utf-8")) > BCRYPT_MAX_BYTES:
            raise ValueError("Password must be at most 72 bytes")
        if not any(c.isalpha() for c in value) or not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one letter and one digit")
        return value


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    role: str
    created_at: datetime
