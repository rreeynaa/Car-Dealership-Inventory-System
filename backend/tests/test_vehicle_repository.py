from decimal import Decimal

import pytest

from app.repositories.vehicle_repository import VehicleFilters, VehicleRepository
from tests.factories import make_vehicle, seed_catalog


def model_names(vehicles) -> list[str]:
    return [vehicle.model for vehicle in vehicles]


def test_add_assigns_id(db_session):
    saved = VehicleRepository(db_session).add(make_vehicle())

    assert saved.id is not None


def test_get_returns_vehicle(db_session):
    repo = VehicleRepository(db_session)
    saved = repo.add(make_vehicle(model="Yaris"))

    assert repo.get(saved.id).model == "Yaris"


def test_get_missing_returns_none(db_session):
    assert VehicleRepository(db_session).get(999999) is None


def test_search_without_filters_returns_all_with_total(db_session):
    seed_catalog(db_session)

    items, total = VehicleRepository(db_session).search(VehicleFilters(), limit=20, offset=0)

    assert model_names(items) == ["Corolla", "RAV4", "Civic", "F-150"]
    assert total == 4


def test_search_paginates_and_reports_full_total(db_session):
    seed_catalog(db_session)

    items, total = VehicleRepository(db_session).search(VehicleFilters(), limit=2, offset=1)

    assert model_names(items) == ["RAV4", "Civic"]
    assert total == 4


@pytest.mark.parametrize(
    ("field", "value", "expected"),
    [
        ("make", "toy", ["Corolla", "RAV4"]),
        ("model", "civ", ["Civic"]),
        ("category", "sedan", ["Corolla", "Civic"]),
    ],
    ids=["make", "model", "category"],
)
def test_text_filters_are_partial_and_case_insensitive(db_session, field, value, expected):
    seed_catalog(db_session)

    items, _ = VehicleRepository(db_session).search(
        VehicleFilters(**{field: value}), limit=20, offset=0
    )

    assert model_names(items) == expected


def test_price_range_is_inclusive(db_session):
    seed_catalog(db_session)
    filters = VehicleFilters(min_price=Decimal("24000"), max_price=Decimal("31000"))

    items, _ = VehicleRepository(db_session).search(filters, limit=20, offset=0)

    assert model_names(items) == ["RAV4", "Civic"]


def test_filters_combine_with_and(db_session):
    seed_catalog(db_session)
    filters = VehicleFilters(make="toyota", category="suv")

    items, total = VehicleRepository(db_session).search(filters, limit=20, offset=0)

    assert model_names(items) == ["RAV4"]
    assert total == 1


def test_search_with_no_match_returns_empty(db_session):
    seed_catalog(db_session)

    items, total = VehicleRepository(db_session).search(
        VehicleFilters(make="Tesla"), limit=20, offset=0
    )

    assert items == []
    assert total == 0


def test_like_wildcards_in_input_are_treated_literally(db_session):
    seed_catalog(db_session)

    items, total = VehicleRepository(db_session).search(
        VehicleFilters(make="%"), limit=20, offset=0
    )

    assert items == []
    assert total == 0


def test_update_persists_changes(db_session):
    repo = VehicleRepository(db_session)
    vehicle = repo.add(make_vehicle())

    repo.update(vehicle, {"price": Decimal("20000.00"), "quantity": 9})

    reloaded = repo.get(vehicle.id)
    assert reloaded.price == Decimal("20000.00")
    assert reloaded.quantity == 9


def test_delete_removes_vehicle(db_session):
    repo = VehicleRepository(db_session)
    vehicle = repo.add(make_vehicle())
    vehicle_id = vehicle.id

    repo.delete(vehicle)

    assert repo.get(vehicle_id) is None
