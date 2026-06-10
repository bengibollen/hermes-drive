from __future__ import annotations

from fastapi import APIRouter, FastAPI, Request

from hermes_drive.api.schemas import LocationIn, SuggestionOut, TripStartIn, TripStateOut
from hermes_drive.storage import InMemoryDriveStore

router = APIRouter()


def get_store(request: Request) -> InMemoryDriveStore:
    return request.app.state.drive_store


@router.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/api/drive/location", response_model=TripStateOut, tags=["drive"])
def ingest_location(payload: LocationIn, request: Request) -> TripStateOut:
    state = get_store(request).trip_service.ingest_location(payload.to_domain())
    return TripStateOut.from_domain(state)


@router.get("/api/drive/state", response_model=TripStateOut, tags=["drive"])
def get_state(request: Request) -> TripStateOut:
    return TripStateOut.from_domain(get_store(request).trip_service.state)


@router.post("/api/drive/trips/start", response_model=TripStateOut, tags=["trips"])
def start_trip(payload: TripStartIn, request: Request) -> TripStateOut:
    state = get_store(request).trip_service.start_trip(payload.device_id)
    return TripStateOut.from_domain(state)


@router.post("/api/drive/trips/stop", response_model=TripStateOut, tags=["trips"])
def stop_trip(request: Request) -> TripStateOut:
    state = get_store(request).trip_service.stop_trip()
    return TripStateOut.from_domain(state)


@router.post("/api/drive/suggest", response_model=SuggestionOut, tags=["drive"])
def suggest(request: Request) -> SuggestionOut:
    state = get_store(request).trip_service.state
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
