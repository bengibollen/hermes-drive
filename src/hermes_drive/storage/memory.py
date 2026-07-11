from __future__ import annotations

from hermes_drive.domain import TripService
from hermes_drive.domain.models import (
    DEFAULT_SUBJECT_ID,
    DEFAULT_VEHICLE_ID,
    TripState,
    VehicleLocation,
)


class InMemoryDriveStore:
    def __init__(self) -> None:
        self._trip_services: dict[tuple[str, str], TripService] = {}

    def get_trip_service(
        self,
        subject_id: str = DEFAULT_SUBJECT_ID,
        vehicle_id: str = DEFAULT_VEHICLE_ID,
    ) -> TripService:
        key = (subject_id, vehicle_id)
        service = self._trip_services.get(key)
        if service is None:
            service = TripService(subject_id=subject_id, vehicle_id=vehicle_id)
            self._trip_services[key] = service
        return service

    def ingest_location(self, location: VehicleLocation) -> TripState:
        return self.get_trip_service(
            subject_id=location.subject_id,
            vehicle_id=location.vehicle_id,
        ).ingest_location(location)
