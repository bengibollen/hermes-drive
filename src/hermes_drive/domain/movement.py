from __future__ import annotations

from hermes_drive.domain.models import MovementStatus, VehicleLocation

MOVING_SPEED_THRESHOLD_KMH = 5


def infer_movement_status(location: VehicleLocation) -> MovementStatus:
    if location.speed_kmh is None:
        return MovementStatus.UNKNOWN
    if location.speed_kmh >= MOVING_SPEED_THRESHOLD_KMH:
        return MovementStatus.MOVING
    return MovementStatus.STOPPED
