from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer, model_validator

MAX_QUANTITY = 1_000_000

Make = Annotated[str, Field(min_length=1, max_length=100)]
Model = Annotated[str, Field(min_length=1, max_length=100)]
Category = Annotated[str, Field(min_length=1, max_length=50)]
# Matches NUMERIC(10, 2) in the database.
Price = Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]
Quantity = Annotated[int, Field(ge=0, le=MAX_QUANTITY)]
# Serialize money as a JSON number (pydantic's default for Decimal is a string).
JsonPrice = Annotated[Decimal, PlainSerializer(float, return_type=float, when_used="json")]


class VehicleCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    make: Make
    model: Model
    category: Category
    price: Price
    quantity: Quantity = 0


class VehicleUpdate(BaseModel):
    """Partial update: send only the fields to change."""

    model_config = ConfigDict(str_strip_whitespace=True)

    make: Make | None = None
    model: Model | None = None
    category: Category | None = None
    price: Price | None = None
    quantity: Quantity | None = None

    @model_validator(mode="after")
    def _require_changes_without_nulls(self) -> "VehicleUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        nulls = sorted(name for name in self.model_fields_set if getattr(self, name) is None)
        if nulls:
            raise ValueError(f"Fields cannot be null: {', '.join(nulls)}")
        return self


class VehicleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    make: str
    model: str
    category: str
    price: JsonPrice
    quantity: int
    created_at: datetime
    updated_at: datetime


class VehicleListOut(BaseModel):
    items: list[VehicleOut]
    total: int
    limit: int
    offset: int
