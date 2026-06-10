from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from hermes_drive.domain.models import (
    MovementStatus,
    TripSession,
    TripState,
    VehicleLocation,
    new_trip_session,
)
from hermes_drive.domain.movement import infer_movement_status


class TripService:
    def __init__(self) -> None:
        self._state = TripState()
        self._active_trip: Optional[TripSession] = None
        self._completed_trips: list[TripSession] = []

    @property
    def state(self) -> TripState:
        return self._state

    def start_trip(self, device_id: str, started_at: Optional[datetime] = None) -> TripState:
        started_at = started_at or datetime.now(timezone.utc)
        self._active_trip = new_trip_session(device_id=device_id, started_at=started_at)
        self._state.device_id = device_id
        self._state.active_trip_id = self._active_trip.id
        self._state.trip_started_at = self._active_trip.started_at
        self._state.accumulated_driving_seconds = 0
        self._state.accumulated_stopped_seconds = 0
        self._state.last_movement_at = None
        self._state.last_stop_at = None
        self._state.movement_status = MovementStatus.UNKNOWN
        self._state.latest_update_at = started_at
        return self._state

    def stop_trip(self, ended_at: Optional[datetime] = None) -> TripState:
        ended_at = ended_at or datetime.now(timezone.utc)
        if self._active_trip is not None:
            self._active_trip.ended_at = ended_at
            self._active_trip.status = "completed"
            self._completed_trips.append(self._active_trip)
            self._active_trip = None

        self._state.active_trip_id = None
        self._state.trip_started_at = None
        self._state.latest_update_at = ended_at
        return self._state

    def ingest_location(self, location: VehicleLocation) -> TripState:
        next_status = infer_movement_status(location)
        previous_location = self._state.latest_location
        previous_status = self._state.movement_status

        if previous_location is not None and previous_status != MovementStatus.UNKNOWN:
            elapsed = (location.timestamp - previous_location.timestamp).total_seconds()
            if elapsed > 0:
                if previous_status == MovementStatus.MOVING:
                    self._state.accumulated_driving_seconds += elapsed
                elif previous_status == MovementStatus.STOPPED:
                    self._state.accumulated_stopped_seconds += elapsed

        self._state.device_id = location.device_id
        self._state.latest_location = location
        self._state.movement_status = next_status
        self._state.latest_update_at = location.timestamp

        if next_status == MovementStatus.MOVING:
            self._state.last_movement_at = location.timestamp
        elif next_status == MovementStatus.STOPPED:
            self._state.last_stop_at = location.timestamp

        return self._state
