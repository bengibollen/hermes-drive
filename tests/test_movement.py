from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from hermes_drive.domain.models import MovementStatus, VehicleLocation
from hermes_drive.domain.movement import infer_movement_status


def location_with_speed(speed_kmh: Optional[float]) -> VehicleLocation:
    return VehicleLocation(
        device_id="car-pi",
        subject_id="default",
        vehicle_id="default",
        timestamp=datetime(2026, 6, 7, 14, 20, tzinfo=timezone.utc),
        latitude=57.7089,
        longitude=11.9746,
        speed_kmh=speed_kmh,
        source="test",
    )


def test_unknown_when_speed_is_absent() -> None:
    assert infer_movement_status(location_with_speed(None)) == MovementStatus.UNKNOWN


def test_stopped_below_threshold() -> None:
    assert infer_movement_status(location_with_speed(4.9)) == MovementStatus.STOPPED


def test_moving_at_threshold() -> None:
    assert infer_movement_status(location_with_speed(5)) == MovementStatus.MOVING
