from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from hermes_drive.domain.models import MovementStatus, TripState, VehicleLocation


class LocationIn(BaseModel):
    device_id: str = Field(alias="deviceId", min_length=1)
    timestamp: datetime
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    speed_kmh: Optional[float] = Field(default=None, alias="speedKmh", ge=0)
    heading: Optional[float] = Field(default=None, ge=0, lt=360)
    accuracy_meters: Optional[float] = Field(default=None, alias="accuracyMeters", ge=0)
    source: str = "unknown"

    def to_domain(self) -> VehicleLocation:
        return VehicleLocation(
            device_id=self.device_id,
            timestamp=self.timestamp,
            latitude=self.lat,
            longitude=self.lon,
            speed_kmh=self.speed_kmh,
            heading=self.heading,
            accuracy_meters=self.accuracy_meters,
            source=self.source,
        )


class TripStartIn(BaseModel):
    device_id: str = Field(alias="deviceId", min_length=1)


class LocationOut(BaseModel):
    device_id: str = Field(serialization_alias="deviceId")
    timestamp: datetime
    lat: float
    lon: float
    speed_kmh: Optional[float] = Field(serialization_alias="speedKmh")
    heading: Optional[float] = None
    accuracy_meters: Optional[float] = Field(serialization_alias="accuracyMeters")
    source: str

    model_config = {"populate_by_name": True}

    @classmethod
    def from_domain(cls, location: VehicleLocation) -> LocationOut:
        return cls(
            device_id=location.device_id,
            timestamp=location.timestamp,
            lat=location.latitude,
            lon=location.longitude,
            speed_kmh=location.speed_kmh,
            heading=location.heading,
            accuracy_meters=location.accuracy_meters,
            source=location.source,
        )


class TripStateOut(BaseModel):
    device_id: Optional[str] = Field(serialization_alias="deviceId")
    active_trip_id: Optional[str] = Field(serialization_alias="activeTripId")
    latest_location: Optional[LocationOut] = Field(serialization_alias="latestLocation")
    trip_started_at: Optional[datetime] = Field(serialization_alias="tripStartedAt")
    last_movement_at: Optional[datetime] = Field(serialization_alias="lastMovementAt")
    last_stop_at: Optional[datetime] = Field(serialization_alias="lastStopAt")
    movement_status: MovementStatus = Field(serialization_alias="movementStatus")
    accumulated_driving_seconds: float = Field(serialization_alias="accumulatedDrivingSeconds")
    accumulated_stopped_seconds: float = Field(serialization_alias="accumulatedStoppedSeconds")
    latest_update_at: Optional[datetime] = Field(serialization_alias="latestUpdateAt")

    model_config = {"populate_by_name": True}

    @classmethod
    def from_domain(cls, state: TripState) -> TripStateOut:
        return cls(
            device_id=state.device_id,
            active_trip_id=state.active_trip_id,
            latest_location=LocationOut.from_domain(state.latest_location)
            if state.latest_location
            else None,
            trip_started_at=state.trip_started_at,
            last_movement_at=state.last_movement_at,
            last_stop_at=state.last_stop_at,
            movement_status=state.movement_status,
            accumulated_driving_seconds=state.accumulated_driving_seconds,
            accumulated_stopped_seconds=state.accumulated_stopped_seconds,
            latest_update_at=state.latest_update_at,
        )


class SuggestionOut(BaseModel):
    message: str
    movement_status: MovementStatus = Field(serialization_alias="movementStatus")
    active_trip_id: Optional[str] = Field(serialization_alias="activeTripId")

    model_config = {"populate_by_name": True}
