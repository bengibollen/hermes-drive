from __future__ import annotations

from fastapi.testclient import TestClient

from hermes_drive.api.app import create_app


def test_health() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_location_ingest_and_state() -> None:
    client = TestClient(create_app())

    payload = {
        "deviceId": "car-pi",
        "timestamp": "2026-06-07T14:20:00Z",
        "lat": 57.7089,
        "lon": 11.9746,
        "speedKmh": 82,
        "heading": 142,
        "accuracyMeters": 8,
        "source": "simulated",
    }
    ingest_response = client.post("/api/drive/location", json=payload)
    state_response = client.get("/api/drive/state")

    assert ingest_response.status_code == 200
    assert ingest_response.json()["movementStatus"] == "moving"
    assert state_response.status_code == 200
    assert state_response.json()["latestLocation"]["deviceId"] == "car-pi"


def test_rejects_invalid_coordinates() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/api/drive/location",
        json={
            "deviceId": "car-pi",
            "timestamp": "2026-06-07T14:20:00Z",
            "lat": 120,
            "lon": 11.9746,
            "source": "simulated",
        },
    )

    assert response.status_code == 422
