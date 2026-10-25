import pytest

from tests.factories import make_vehicle, seed_catalog

URL = "/api/vehicles"


def purchase(client, vehicle_id, headers=None):
    return client.post(f"{URL}/{vehicle_id}/purchase", headers=headers)


def restock(client, vehicle_id, body, headers=None):
    return client.post(f"{URL}/{vehicle_id}/restock", json=body, headers=headers)


# ---------- purchase ----------


def test_purchase_decrements_quantity(client, user_headers, db_session):
    vehicle = seed_catalog(db_session)[0]  # quantity 5

    response = purchase(client, vehicle.id, user_headers)

    assert response.status_code == 200
    assert response.json()["quantity"] == 4


def test_purchasing_last_unit_then_again_returns_409(client, user_headers, db_session):
    vehicle = make_vehicle(quantity=1)
    db_session.add(vehicle)
    db_session.commit()

    assert purchase(client, vehicle.id, user_headers).json()["quantity"] == 0
    second = purchase(client, vehicle.id, user_headers)

    assert second.status_code == 409
    assert "out of stock" in second.json()["detail"].lower()


def test_purchase_sold_out_vehicle_returns_409(client, user_headers, db_session):
    vehicle = make_vehicle(quantity=0)
    db_session.add(vehicle)
    db_session.commit()

    assert purchase(client, vehicle.id, user_headers).status_code == 409


def test_purchase_unknown_vehicle_returns_404(client, user_headers):
    assert purchase(client, 999999, user_headers).status_code == 404


def test_purchase_requires_authentication(client):
    assert purchase(client, 1).status_code == 401


# ---------- restock ----------


def test_admin_can_restock(client, admin_headers, db_session):
    vehicle = seed_catalog(db_session)[0]  # quantity 5

    response = restock(client, vehicle.id, {"quantity": 10}, admin_headers)

    assert response.status_code == 200
    assert response.json()["quantity"] == 15


def test_restocked_vehicle_can_be_purchased_again(client, admin_headers, user_headers, db_session):
    vehicle = make_vehicle(quantity=0)
    db_session.add(vehicle)
    db_session.commit()

    restock(client, vehicle.id, {"quantity": 2}, admin_headers)

    assert purchase(client, vehicle.id, user_headers).status_code == 200


def test_regular_user_cannot_restock(client, user_headers, db_session):
    vehicle = seed_catalog(db_session)[0]

    assert restock(client, vehicle.id, {"quantity": 1}, user_headers).status_code == 403


def test_restock_unknown_vehicle_returns_404(client, admin_headers):
    assert restock(client, 999999, {"quantity": 1}, admin_headers).status_code == 404


def test_restock_requires_authentication(client):
    assert restock(client, 1, {"quantity": 1}).status_code == 401


@pytest.mark.parametrize(
    "quantity",
    [0, -5, 1_000_001],
    ids=["zero", "negative", "too-large"],
)
def test_restock_rejects_invalid_amount(client, admin_headers, db_session, quantity):
    vehicle = seed_catalog(db_session)[0]

    response = restock(client, vehicle.id, {"quantity": quantity}, admin_headers)

    assert response.status_code == 422


def test_restock_rejects_missing_body(client, admin_headers, db_session):
    vehicle = seed_catalog(db_session)[0]

    assert restock(client, vehicle.id, {}, admin_headers).status_code == 422
