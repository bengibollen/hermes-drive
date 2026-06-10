from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Optional

from hermes_drive.domain import MovementStatus, TripService, VehicleLocation


def make_location(timestamp: datetime, speed_kmh: Optional[float]) -> VehicleLocation:
    return VehicleLocation(
        device_id="car-pi",
        timestamp=timestamp,
        latitude=57.7089,
        longitude=11.9746,
        speed_kmh=speed_kmh,
        source="test",
    )


def test_start_and_stop_trip_sets_active_trip_id() -> None:
    service = TripService()

    started = service.start_trip("car-pi", datetime(2026, 6, 7, 12, tzinfo=timezone.utc))
    assert started.active_trip_id is not None
    assert started.device_id == "car-pi"

    stopped = service.stop_trip(datetime(2026, 6, 7, 13, tzinfo=timezone.utc))
    assert stopped.active_trip_id is None
    assert stopped.trip_started_at is None


def test_ingest_location_updates_movement_status() -> None:
    service = TripService()
    now = datetime(2026, 6, 7, 14, 20, tzinfo=timezone.utc)

    state = service.ingest_location(make_location(now, 82))

    assert state.latest_location is not None
    assert state.movement_status == MovementStatus.MOVING
    assert state.last_movement_at == now


def test_duration_accumulates_from_previous_known_status() -> None:
    service = TripService()
    first = datetime(2026, 6, 7, 14, 20, tzinfo=timezone.utc)

    service.ingest_location(make_location(first, 82))
    service.ingest_location(make_location(first + timedelta(minutes=2), 80))
    state = service.ingest_location(make_location(first + timedelta(minutes=5), 0))

    assert state.movement_status == MovementStatus.STOPPED
    assert state.accumulated_driving_seconds == 300
    assert state.accumulated_stopped_seconds == 0

    state = service.ingest_location(make_location(first + timedelta(minutes=7), 0))
    assert state.accumulated_driving_seconds == 300
    assert state.accumulated_stopped_seconds == 120


def test_unknown_speed_does_not_accumulate_duration() -> None:
    service = TripService()
    first = datetime(2026, 6, 7, 14, 20, tzinfo=timezone.utc)

    service.ingest_location(make_location(first, None))
    state = service.ingest_location(make_location(first + timedelta(minutes=2), 0))

    assert state.movement_status == MovementStatus.STOPPED
    assert state.accumulated_driving_seconds == 0
    assert state.accumulated_stopped_seconds == 0
