"""Populate the database with demo accounts and vehicles.

Usage (from backend/):  python -m app.seed
The script is idempotent: existing accounts and vehicles are never modified.
"""

import sys
from dataclasses import dataclass
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models import Role, User, Vehicle


@dataclass(frozen=True)
class SeedAccount:
    email: str
    password: str
    role: Role


@dataclass(frozen=True)
class SeedResult:
    users_created: int
    vehicles_created: int


def _car(make: str, model: str, category: str, price: str, quantity: int) -> dict:
    return {
        "make": make,
        "model": model,
        "category": category,
        "price": Decimal(price),
        "quantity": quantity,
    }


# Includes two sold-out vehicles so the disabled Purchase button is visible in the UI.
SAMPLE_VEHICLES: list[dict] = [
    _car("Toyota", "Corolla", "Sedan", "22450.00", 12),
    _car("Toyota", "RAV4", "SUV", "29800.00", 8),
    _car("Toyota", "Camry", "Sedan", "27500.00", 6),
    _car("Honda", "Civic", "Sedan", "24200.00", 10),
    _car("Honda", "CR-V", "SUV", "31500.00", 7),
    _car("Ford", "F-150", "Truck", "38900.00", 5),
    _car("Ford", "Mustang", "Coupe", "42500.00", 3),
    _car("Chevrolet", "Silverado", "Truck", "41200.00", 0),
    _car("Tesla", "Model 3", "Electric", "40240.00", 4),
    _car("Kia", "EV6", "Electric", "44900.00", 0),
    _car("BMW", "3 Series", "Sedan", "46800.00", 2),
    _car("Mazda", "MX-5 Miata", "Convertible", "29900.00", 1),
    _car("Hyundai", "Tucson", "SUV", "28900.00", 9),
    _car("Subaru", "Outback", "Wagon", "30100.00", 6),
]


def seed_database(db: Session, accounts: list[SeedAccount], vehicles: list[dict]) -> SeedResult:
    """Insert whatever is missing and report how much was created."""
    users_created = 0
    for account in accounts:
        email = account.email.lower()
        if db.scalar(select(User.id).where(User.email == email)) is None:
            db.add(
                User(
                    email=email,
                    hashed_password=hash_password(account.password),
                    role=account.role.value,
                )
            )
            db.flush()
            users_created += 1

    vehicles_created = 0
    for data in vehicles:
        existing = db.scalar(
            select(Vehicle.id)
            .where(Vehicle.make == data["make"], Vehicle.model == data["model"])
            .limit(1)
        )
        if existing is None:
            db.add(Vehicle(**data))
            db.flush()
            vehicles_created += 1

    db.commit()
    return SeedResult(users_created, vehicles_created)


def accounts_from_settings() -> list[SeedAccount]:
    return [
        SeedAccount(settings.seed_admin_email, settings.seed_admin_password, Role.ADMIN),
        SeedAccount(settings.seed_user_email, settings.seed_user_password, Role.USER),
    ]


def main(argv: list[str] | None = None) -> None:
    args = sys.argv[1:] if argv is None else argv
    if "--if-enabled" in args and not settings.seed_on_startup:
        print("Seeding skipped (SEED_ON_STARTUP is not true).")
        return
    with SessionLocal() as db:
        result = seed_database(db, accounts_from_settings(), SAMPLE_VEHICLES)
    print(
        f"Seed complete: {result.users_created} users and "
        f"{result.vehicles_created} vehicles created."
    )


if __name__ == "__main__":
    main()
