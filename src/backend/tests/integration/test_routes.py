from flask import current_app


def test_index_renders(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"index" in resp.data or b"<!DOCTYPE html" in resp.data


def test_get_location_info_success(client, app):
    # Inject fake place_service
    from src.backend.tests.conftest import FakePlaceService

    app.extensions["services"]["place_service"] = FakePlaceService(response="OK")

    resp = client.post(
        "/get_location_info",
        json={"latitude": 10.0, "longitude": 20.0},
    )
    assert resp.status_code == 200
    assert resp.is_json
    assert resp.get_json()["info"].startswith("OK")


def test_get_location_info_validation_error(client):
    resp = client.post("/get_location_info", json={"latitude": 1000})
    assert resp.status_code == 400
    assert resp.is_json
    assert "error" in resp.get_json()
