from __future__ import annotations

from fastapi import APIRouter, FastAPI, Query, Request

from hermes_drive.api.schemas import LocationIn, SuggestionOut, TripStartIn, TripStateOut
from hermes_drive.domain.models import DEFAULT_SUBJECT_ID, DEFAULT_VEHICLE_ID
from hermes_drive.storage import InMemoryDriveStore

router = APIRouter()


def get_store(request: Request) -> InMemoryDriveStore:
    return request.app.state.drive_store


@router.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/api/drive/location", response_model=TripStateOut, tags=["drive"])
def ingest_location(payload: LocationIn, request: Request) -> TripStateOut:
    state = get_store(request).ingest_location(payload.to_domain())
    return TripStateOut.from_domain(state)


@router.get("/api/drive/state", response_model=TripStateOut, tags=["drive"])
def get_state(
    request: Request,
    subject_id: str = Query(DEFAULT_SUBJECT_ID, alias="subjectId"),
    vehicle_id: str = Query(DEFAULT_VEHICLE_ID, alias="vehicleId"),
) -> TripStateOut:
    return TripStateOut.from_domain(
        get_store(request).get_trip_service(subject_id=subject_id, vehicle_id=vehicle_id).state
    )


@router.post("/api/drive/trips/start", response_model=TripStateOut, tags=["trips"])
def start_trip(payload: TripStartIn, request: Request) -> TripStateOut:
    state = (
        get_store(request)
        .get_trip_service(
            subject_id=payload.subject_id,
            vehicle_id=payload.vehicle_id,
        )
        .start_trip(payload.device_id)
    )
    return TripStateOut.from_domain(state)


@router.post("/api/drive/trips/stop", response_model=TripStateOut, tags=["trips"])
def stop_trip(
    request: Request,
    subject_id: str = Query(DEFAULT_SUBJECT_ID, alias="subjectId"),
    vehicle_id: str = Query(DEFAULT_VEHICLE_ID, alias="vehicleId"),
) -> TripStateOut:
    state = (
        get_store(request)
        .get_trip_service(
            subject_id=subject_id,
            vehicle_id=vehicle_id,
        )
        .stop_trip()
    )
    return TripStateOut.from_domain(state)


@router.post("/api/drive/suggest", response_model=SuggestionOut, tags=["drive"])
def suggest(
    request: Request,
    subject_id: str = Query(DEFAULT_SUBJECT_ID, alias="subjectId"),
    vehicle_id: str = Query(DEFAULT_VEHICLE_ID, alias="vehicleId"),
) -> SuggestionOut:
    state = (
        get_store(request)
        .get_trip_service(
            subject_id=subject_id,
            vehicle_id=vehicle_id,
        )
        .state
    )
    if state.active_trip_id is None:
        message = "No active trip."
    elif state.latest_location is None:
        message = "Active trip has no recent location yet."
    elif state.movement_status == "moving":
        message = "Vehicle is moving. Keep suggestions lightweight."
    elif state.movement_status == "stopped":
        message = "Vehicle is stopped. Suggestions may be appropriate."
    else:
        message = "Vehicle movement is unknown."

    return SuggestionOut(
        subject_id=state.subject_id,
        vehicle_id=state.vehicle_id,
        message=message,
        movement_status=state.movement_status,
        active_trip_id=state.active_trip_id,
    )


def create_app() -> FastAPI:
    app = FastAPI(
        title="Hermes Drive",
        version="0.1.0",
        description="Vehicle trip context and GPS/location ingest service for Hermes.",
    )
    app.state.drive_store = InMemoryDriveStore()
    app.include_router(router)
    return app
