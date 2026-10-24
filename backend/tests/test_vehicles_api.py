import pytest

from tests.factories import make_vehicle, seed_catalog, vehicle_payload

URL = "/api/vehicles"


# ---------- create ----------


def test_admin_can_create_vehicle(client, admin_headers):
    response = client.post(URL, json=vehicle_payload(), headers=admin_headers)

    assert response.status_code == 201
    body = response.json()
    assert isinstance(body["id"], int)
    assert body["make"] == "Toyota"
    assert body["price"] == 22000.0
    assert body["quantity"] == 5


def test_regular_user_cannot_create_vehicle(client, user_headers):
    response = client.post(URL, json=vehicle_payload(), headers=user_headers)

    assert response.status_code == 403


def test_create_requires_authentication(client):
    assert client.post(URL, json=vehicle_payload()).status_code == 401


@pytest.mark.parametrize(
    "overrides",
    [
        {"price": 0},
        {"price": -5},
        {"price": 12.345},
        {"quantity": -1},
        {"quantity": 1_000_001},
        {"make": ""},
        {"make": "   "},
    ],
    ids=[
        "zero-price",
        "negative-price",
        "too-many-decimals",
        "negative-quantity",
        "quantity-too-large",
        "blank-make",
        "whitespace-make",
    ],
)
def test_create_rejects_invalid_data(client, admin_headers, overrides):
    response = client.post(URL, json=vehicle_payload(**overrides), headers=admin_headers)

    assert response.status_code == 422


def test_create_rejects_missing_field(client, admin_headers):
    payload = vehicle_payload()
    del payload["model"]

    assert client.post(URL, json=payload, headers=admin_headers).status_code == 422


# ---------- list ----------


def test_any_authenticated_user_can_list_vehicles(client, user_headers, db_session):
    seed_catalog(db_session)

    response = client.get(URL, headers=user_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 4
    assert len(body["items"]) == 4
    assert body["limit"] == 20
    assert body["offset"] == 0


def test_list_requires_authentication(client):
    assert client.get(URL).status_code == 401


def test_list_includes_out_of_stock_vehicles(client, user_headers, db_session):
    db_session.add(make_vehicle(model="Sold Out", quantity=0))
    db_session.commit()

    items = client.get(URL, headers=user_headers).json()["items"]

    assert [item["quantity"] for item in items] == [0]


def test_list_respects_limit_and_offset(client, user_headers, db_session):
    seed_catalog(db_session)

    body = client.get(URL, params={"limit": 2, "offset": 1}, headers=user_headers).json()

    assert [item["model"] for item in body["items"]] == ["RAV4", "Civic"]
    assert body["total"] == 4
    assert body["limit"] == 2
    assert body["offset"] == 1


@pytest.mark.parametrize(
    ("name", "value"),
    [("limit", 0), ("limit", 101), ("offset", -1)],
    ids=["limit-zero", "limit-too-large", "negative-offset"],
)
def test_list_rejects_invalid_paging(client, user_headers, name, value):
    response = client.get(URL, params={name: value}, headers=user_headers)

    assert response.status_code == 422


# ---------- get one ----------


def test_get_vehicle_returns_it(client, user_headers, db_session):
    vehicle = seed_catalog(db_session)[1]

    response = client.get(f"{URL}/{vehicle.id}", headers=user_headers)

    assert response.status_code == 200
    assert response.json()["model"] == "RAV4"


def test_get_unknown_vehicle_returns_404(client, user_headers):
    assert client.get(f"{URL}/999999", headers=user_headers).status_code == 404


# ---------- update ----------


def test_admin_can_partially_update_vehicle(client, admin_headers, db_session):
    vehicle = seed_catalog(db_session)[0]

    response = client.put(
        f"{URL}/{vehicle.id}", json={"price": 20500.0, "quantity": 9}, headers=admin_headers
    )

    assert response.status_code == 200
    body = response.json()
    assert body["price"] == 20500.0
    assert body["quantity"] == 9
    assert body["make"] == "Toyota"  # untouched fields are preserved


def test_regular_user_cannot_update_vehicle(client, user_headers, db_session):
    vehicle = seed_catalog(db_session)[0]

    response = client.put(f"{URL}/{vehicle.id}", json={"quantity": 1}, headers=user_headers)

    assert response.status_code == 403


def test_update_unknown_vehicle_returns_404(client, admin_headers):
    response = client.put(f"{URL}/999999", json={"quantity": 1}, headers=admin_headers)

    assert response.status_code == 404


def test_update_rejects_empty_body(client, admin_headers, db_session):
    vehicle = seed_catalog(db_session)[0]

    response = client.put(f"{URL}/{vehicle.id}", json={}, headers=admin_headers)

    assert response.status_code == 422


def test_update_rejects_null_values(client, admin_headers, db_session):
    vehicle = seed_catalog(db_session)[0]

    response = client.put(f"{URL}/{vehicle.id}", json={"make": None}, headers=admin_headers)

    assert response.status_code == 422


def test_update_rejects_invalid_price(client, admin_headers, db_session):
    vehicle = seed_catalog(db_session)[0]

    response = client.put(f"{URL}/{vehicle.id}", json={"price": 0}, headers=admin_headers)

    assert response.status_code == 422


# ---------- delete ----------


def test_admin_can_delete_vehicle(client, admin_headers, db_session):
    vehicle_id = seed_catalog(db_session)[0].id

    response = client.delete(f"{URL}/{vehicle_id}", headers=admin_headers)

    assert response.status_code == 204
    assert client.get(f"{URL}/{vehicle_id}", headers=admin_headers).status_code == 404


def test_regular_user_cannot_delete_vehicle(client, user_headers, db_session):
    vehicle_id = seed_catalog(db_session)[0].id

    assert client.delete(f"{URL}/{vehicle_id}", headers=user_headers).status_code == 403


def test_delete_unknown_vehicle_returns_404(client, admin_headers):
    assert client.delete(f"{URL}/999999", headers=admin_headers).status_code == 404


def test_delete_requires_authentication(client):
    assert client.delete(f"{URL}/1").status_code == 401
