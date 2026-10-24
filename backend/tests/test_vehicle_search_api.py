import pytest

from tests.factories import seed_catalog

URL = "/api/vehicles/search"


def model_names(response) -> list[str]:
    return [item["model"] for item in response.json()["items"]]


@pytest.mark.parametrize(
    ("param", "value", "expected"),
    [
        ("make", "toy", ["Corolla", "RAV4"]),
        ("model", "civ", ["Civic"]),
        ("category", "sedan", ["Corolla", "Civic"]),
    ],
    ids=["make", "model", "category"],
)
def test_search_text_fields_are_partial_and_case_insensitive(
    client, user_headers, db_session, param, value, expected
):
    seed_catalog(db_session)

    response = client.get(URL, params={param: value}, headers=user_headers)

    assert response.status_code == 200
    assert model_names(response) == expected


def test_search_by_inclusive_price_range(client, user_headers, db_session):
    seed_catalog(db_session)

    response = client.get(
        URL, params={"min_price": 24000, "max_price": 31000}, headers=user_headers
    )

    assert model_names(response) == ["RAV4", "Civic"]


def test_search_combines_filters(client, user_headers, db_session):
    seed_catalog(db_session)

    response = client.get(URL, params={"make": "toyota", "category": "suv"}, headers=user_headers)

    assert model_names(response) == ["RAV4"]
    assert response.json()["total"] == 1


def test_search_with_no_match_returns_empty_page(client, user_headers, db_session):
    seed_catalog(db_session)

    body = client.get(URL, params={"make": "Tesla"}, headers=user_headers).json()

    assert body["items"] == []
    assert body["total"] == 0


def test_search_rejects_inverted_price_range(client, user_headers):
    response = client.get(
        URL, params={"min_price": 50000, "max_price": 10000}, headers=user_headers
    )

    assert response.status_code == 422


def test_search_without_params_returns_everything(client, user_headers, db_session):
    """Also proves '/search' is not swallowed by the '/{vehicle_id}' route."""
    seed_catalog(db_session)

    response = client.get(URL, headers=user_headers)

    assert response.status_code == 200
    assert response.json()["total"] == 4


def test_search_requires_authentication(client):
    assert client.get(URL).status_code == 401


def test_search_is_paginated(client, user_headers, db_session):
    seed_catalog(db_session)

    response = client.get(
        URL, params={"category": "sedan", "limit": 1, "offset": 1}, headers=user_headers
    )

    assert model_names(response) == ["Civic"]
    assert response.json()["total"] == 2
