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
    assert ingest_response.json()["subjectId"] == "default"
    assert ingest_response.json()["vehicleId"] == "default"
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


def test_tracks_state_by_subject_and_vehicle() -> None:
    client = TestClient(create_app())

    pi_payload = {
        "deviceId": "car-pi",
        "subjectId": "danne",
        "vehicleId": "car",
        "timestamp": "2026-06-07T14:20:00Z",
        "lat": 57.7089,
        "lon": 11.9746,
        "speedKmh": 82,
        "source": "gpsd",
    }
    phone_payload = {
        "deviceId": "iphone-danne",
        "subjectId": "danne",
        "vehicleId": "phone",
        "timestamp": "2026-06-07T14:21:00Z",
        "lat": 57.7100,
        "lon": 11.9800,
        "speedKmh": 4,
        "source": "iphone",
    }

    assert client.post("/api/drive/location", json=pi_payload).status_code == 200
    assert client.post("/api/drive/location", json=phone_payload).status_code == 200

    car_state = client.get(
        "/api/drive/state",
        params={"subjectId": "danne", "vehicleId": "car"},
    ).json()
    phone_state = client.get(
        "/api/drive/state",
        params={"subjectId": "danne", "vehicleId": "phone"},
    ).json()

    assert car_state["latestLocation"]["deviceId"] == "car-pi"
    assert car_state["movementStatus"] == "moving"
    assert phone_state["latestLocation"]["deviceId"] == "iphone-danne"
    assert phone_state["movementStatus"] == "stopped"


def test_food_endpoint_returns_json_response() -> None:
    client = TestClient(create_app())
    payload = {
        "deviceId": "car-pi",
        "subjectId": "danne",
        "vehicleId": "car",
        "timestamp": "2026-06-07T14:20:00Z",
        "lat": 57.7089,
        "lon": 11.9746,
        "speedKmh": 82,
        "heading": 142,
        "accuracyMeters": 8,
        "source": "gpsd",
    }

    response = client.post(
        "/api/drive/food",
        params={"subjectId": "danne", "vehicleId": "car"},
        json=payload,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["intent"] == "food"
    assert body["subjectId"] == "danne"
    assert body["vehicleId"] == "car"
    assert body["movementStatus"] == "moving"
    assert body["hasRecentLocation"] is True
    assert body["speechSupported"] is False
    assert "Food request noted" in body["message"]

    state = client.get(
        "/api/drive/state",
        params={"subjectId": "danne", "vehicleId": "car"},
    ).json()
    assert state["latestLocation"]["deviceId"] == "car-pi"
    assert state["latestLocation"]["heading"] == 142


def test_parking_endpoint_can_return_text_response() -> None:
    client = TestClient(create_app())

    response = client.post("/api/drive/parking", params={"responseMode": "text"})

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert response.text == (
        "I do not have a recent location yet, so I cannot suggest parking or a rest stop."
    )


def test_speech_response_mode_is_explicitly_not_implemented() -> None:
    client = TestClient(create_app())

    response = client.post("/api/drive/food", params={"responseMode": "speech"})

    assert response.status_code == 501
    body = response.json()
    assert body["intent"] == "food"
    assert body["speechSupported"] is False
    assert "Speech responses are not implemented yet" in body["message"]
