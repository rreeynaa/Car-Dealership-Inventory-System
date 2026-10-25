from decimal import Decimal

from sqlalchemy import func, select

from app.core.security import verify_password
from app.models import Role, User, Vehicle
from app.schemas.vehicle import VehicleCreate
from app.seed import SAMPLE_VEHICLES, SeedAccount, seed_database
from tests.factories import make_vehicle

ADMIN = SeedAccount("admin@example.com", "Adm1n!pass", Role.ADMIN)
SHOPPER = SeedAccount("shopper@example.com", "Sh0pper!pass", Role.USER)
FEW_VEHICLES = SAMPLE_VEHICLES[:3]


def count(db, model) -> int:
    return db.scalar(select(func.count()).select_from(model))


def test_seed_creates_admin_with_hashed_password(db_session):
    seed_database(db_session, [ADMIN], [])

    admin = db_session.scalar(select(User).where(User.email == ADMIN.email))
    assert admin.role == "admin"
    assert admin.hashed_password != ADMIN.password
    assert verify_password(ADMIN.password, admin.hashed_password)


def test_seed_creates_regular_user(db_session):
    seed_database(db_session, [SHOPPER], [])

    user = db_session.scalar(select(User).where(User.email == SHOPPER.email))
    assert user.role == "user"


def test_seed_creates_vehicles(db_session):
    result = seed_database(db_session, [], FEW_VEHICLES)

    assert result.vehicles_created == 3
    assert count(db_session, Vehicle) == 3


def test_seed_is_idempotent(db_session):
    seed_database(db_session, [ADMIN, SHOPPER], FEW_VEHICLES)

    second = seed_database(db_session, [ADMIN, SHOPPER], FEW_VEHICLES)

    assert second.users_created == 0
    assert second.vehicles_created == 0
    assert count(db_session, User) == 2
    assert count(db_session, Vehicle) == 3


def test_seed_never_overwrites_existing_account(db_session):
    db_session.add(User(email=ADMIN.email, hashed_password="existing", role="user"))
    db_session.commit()

    result = seed_database(db_session, [ADMIN], [])

    user = db_session.scalar(select(User).where(User.email == ADMIN.email))
    assert result.users_created == 0
    assert user.hashed_password == "existing"
    assert user.role == "user"


def test_seed_skips_vehicle_already_in_catalog(db_session):
    first = FEW_VEHICLES[0]
    db_session.add(make_vehicle(make=first["make"], model=first["model"]))
    db_session.commit()

    result = seed_database(db_session, [], FEW_VEHICLES)

    assert result.vehicles_created == 2


def test_sample_catalog_is_valid_and_varied():
    for vehicle in SAMPLE_VEHICLES:
        VehicleCreate(**vehicle)  # raises if it would violate the API's own rules
    assert len(SAMPLE_VEHICLES) >= 12
    assert len({v["category"] for v in SAMPLE_VEHICLES}) >= 4
    assert any(v["quantity"] == 0 for v in SAMPLE_VEHICLES)  # shows the disabled Purchase button
    assert all(isinstance(v["price"], Decimal) for v in SAMPLE_VEHICLES)
