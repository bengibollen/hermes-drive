from __future__ import annotations

from hermes_drive.domain import TripService


class InMemoryDriveStore:
    def __init__(self) -> None:
        self.trip_service = TripService()
