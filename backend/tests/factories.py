"""Helpers for building test data."""

from decimal import Decimal

from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.models import User, Vehicle


def auth_headers_for(user: User) -> dict[str, str]:
    """Authorization header carrying a valid JWT for the given user."""
    token = create_access_token(subject=str(user.id), role=user.role)
    return {"Authorization": f"Bearer {token}"}


def make_vehicle(**overrides) -> Vehicle:
    """An unsaved Vehicle with sensible defaults."""
    fields = {
        "make": "Toyota",
        "model": "Corolla",
        "category": "Sedan",
        "price": Decimal("22000.00"),
        "quantity": 5,
    }
    fields.update(overrides)
    return Vehicle(**fields)


def vehicle_payload(**overrides) -> dict:
    """A valid JSON body for creating a vehicle."""
    payload = {
        "make": "Toyota",
        "model": "Corolla",
        "category": "Sedan",
        "price": 22000.0,
        "quantity": 5,
    }
    payload.update(overrides)
    return payload


def seed_catalog(session: Session) -> list[Vehicle]:
    """Insert four vehicles. Ids ascend in the order listed here."""
    vehicles = [
        make_vehicle(make="Toyota", model="Corolla", category="Sedan", price=Decimal("22000")),
        make_vehicle(make="Toyota", model="RAV4", category="SUV", price=Decimal("31000")),
        make_vehicle(make="Honda", model="Civic", category="Sedan", price=Decimal("24000")),
        make_vehicle(make="Ford", model="F-150", category="Truck", price=Decimal("45000")),
    ]
    session.add_all(vehicles)
    session.commit()
    return vehicles
