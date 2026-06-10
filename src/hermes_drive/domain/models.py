from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import uuid4


class MovementStatus(str, Enum):
    UNKNOWN = "unknown"
    MOVING = "moving"
    STOPPED = "stopped"


@dataclass(frozen=True)
class VehicleLocation:
    device_id: str
    timestamp: datetime
    latitude: float
    longitude: float
    speed_kmh: Optional[float] = None
    heading: Optional[float] = None
    accuracy_meters: Optional[float] = None
    source: str = "unknown"


@dataclass
class TripSession:
    id: str
    device_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    status: str = "active"


@dataclass
class TripState:
    device_id: Optional[str] = None
    active_trip_id: Optional[str] = None
    latest_location: Optional[VehicleLocation] = None
    trip_started_at: Optional[datetime] = None
    last_movement_at: Optional[datetime] = None
    last_stop_at: Optional[datetime] = None
    movement_status: MovementStatus = MovementStatus.UNKNOWN
    accumulated_driving_seconds: float = 0
    accumulated_stopped_seconds: float = 0
    latest_update_at: Optional[datetime] = None


def new_trip_session(device_id: str, started_at: Optional[datetime] = None) -> TripSession:
    return TripSession(
        id=str(uuid4()),
        device_id=device_id,
        started_at=started_at or datetime.now(timezone.utc),
    )
