from concurrent.futures import ThreadPoolExecutor

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models import Vehicle
from app.repositories.vehicle_repository import VehicleRepository
from tests.factories import make_vehicle


def test_decrement_reduces_quantity_by_one(db_session):
    repo = VehicleRepository(db_session)
    vehicle = repo.add(make_vehicle(quantity=5))

    updated = repo.decrement_stock(vehicle.id)

    assert updated is not None
    assert updated.quantity == 4


def test_decrement_at_zero_returns_none_and_keeps_zero(db_session):
    repo = VehicleRepository(db_session)
    vehicle = repo.add(make_vehicle(quantity=0))

    assert repo.decrement_stock(vehicle.id) is None
    assert repo.get(vehicle.id).quantity == 0


def test_decrement_unknown_vehicle_returns_none(db_session):
    assert VehicleRepository(db_session).decrement_stock(999999) is None


def test_increment_adds_to_quantity(db_session):
    repo = VehicleRepository(db_session)
    vehicle = repo.add(make_vehicle(quantity=2))

    updated = repo.increment_stock(vehicle.id, 10)

    assert updated is not None
    assert updated.quantity == 12


def test_increment_unknown_vehicle_returns_none(db_session):
    assert VehicleRepository(db_session).increment_stock(999999, 5) is None


def test_concurrent_purchases_never_oversell(engine):
    """Ten buyers race for three cars: exactly three may succeed.

    This test commits for real on separate connections (the rollback fixture
    cannot be used for concurrency), so it cleans up after itself.
    """
    with Session(engine) as setup:
        vehicle_id = VehicleRepository(setup).add(make_vehicle(quantity=3)).id

    def attempt(_: int) -> bool:
        with Session(engine) as session:
            return VehicleRepository(session).decrement_stock(vehicle_id) is not None

    try:
        with ThreadPoolExecutor(max_workers=10) as pool:
            results = list(pool.map(attempt, range(10)))
        with Session(engine) as check:
            remaining = check.get(Vehicle, vehicle_id).quantity
        assert results.count(True) == 3
        assert remaining == 0
    finally:
        with Session(engine) as cleanup:
            cleanup.execute(delete(Vehicle).where(Vehicle.id == vehicle_id))
            cleanup.commit()
