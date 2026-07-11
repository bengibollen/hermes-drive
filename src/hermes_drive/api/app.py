from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Body, FastAPI, Query, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, PlainTextResponse, Response

from hermes_drive.api.schemas import (
    DriveIntent,
    DriveIntentOut,
    LocationIn,
    ResponseMode,
    SuggestionOut,
    TripStartIn,
    TripStateOut,
)
from hermes_drive.domain.models import DEFAULT_SUBJECT_ID, DEFAULT_VEHICLE_ID
from hermes_drive.domain.trip_service import TripService
from hermes_drive.storage import InMemoryDriveStore

router = APIRouter()


def get_store(request: Request) -> InMemoryDriveStore:
    return request.app.state.drive_store


def get_trip_service(
    request: Request,
    subject_id: str,
    vehicle_id: str,
) -> TripService:
    return get_store(request).get_trip_service(subject_id=subject_id, vehicle_id=vehicle_id)


def render_intent_response(
    intent_out: DriveIntentOut,
    response_mode: ResponseMode,
) -> Response:
    if response_mode == ResponseMode.TEXT:
        return PlainTextResponse(intent_out.message)

    if response_mode == ResponseMode.SPEECH:
        content = intent_out.model_copy(
            update={
                "message": (
                    f"Speech responses are not implemented yet. Text response: {intent_out.message}"
                ),
                "speech_supported": False,
            }
        )
        return JSONResponse(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            content=jsonable_encoder(content.model_dump(by_alias=True)),
        )

    return JSONResponse(content=jsonable_encoder(intent_out.model_dump(by_alias=True)))


def build_intent_response(
    service: TripService,
    intent: DriveIntent,
) -> DriveIntentOut:
    state = service.state
    has_recent_location = state.latest_location is not None

    if intent == DriveIntent.FOOD:
        if not has_recent_location:
            message = "I do not have a recent location yet, so I cannot suggest food nearby."
        elif state.movement_status == "moving":
            message = "Food request noted. I will look for a suitable stop near the current route."
        else:
            message = (
                "Food request noted. The vehicle is stopped, so nearby options are appropriate."
            )
    else:
        if not has_recent_location:
            message = (
                "I do not have a recent location yet, so I cannot suggest parking or a rest stop."
            )
        elif state.movement_status == "moving":
            message = "Parking request noted. I will look for a safe place to stop or rest."
        else:
            message = (
                "Parking request noted. The vehicle is stopped, so nearby parking is appropriate."
            )

    return DriveIntentOut(
        subject_id=state.subject_id,
        vehicle_id=state.vehicle_id,
        intent=intent,
        message=message,
        movement_status=state.movement_status,
        active_trip_id=state.active_trip_id,
        has_recent_location=has_recent_location,
        speech_supported=False,
    )


def get_intent_service(
    request: Request,
    payload: Optional[LocationIn],
    subject_id: str,
    vehicle_id: str,
) -> TripService:
    store = get_store(request)
    if payload is None:
        return store.get_trip_service(subject_id=subject_id, vehicle_id=vehicle_id)

    location = payload.to_domain()
    store.ingest_location(location)
    return store.get_trip_service(
        subject_id=location.subject_id,
        vehicle_id=location.vehicle_id,
    )


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
    return TripStateOut.from_domain(get_trip_service(request, subject_id, vehicle_id).state)


@router.post("/api/drive/trips/start", response_model=TripStateOut, tags=["trips"])
def start_trip(payload: TripStartIn, request: Request) -> TripStateOut:
    state = get_trip_service(
        request,
        subject_id=payload.subject_id,
        vehicle_id=payload.vehicle_id,
    ).start_trip(payload.device_id)
    return TripStateOut.from_domain(state)


@router.post("/api/drive/trips/stop", response_model=TripStateOut, tags=["trips"])
def stop_trip(
    request: Request,
    subject_id: str = Query(DEFAULT_SUBJECT_ID, alias="subjectId"),
    vehicle_id: str = Query(DEFAULT_VEHICLE_ID, alias="vehicleId"),
) -> TripStateOut:
    state = get_trip_service(
        request,
        subject_id=subject_id,
        vehicle_id=vehicle_id,
    ).stop_trip()
    return TripStateOut.from_domain(state)


@router.post("/api/drive/suggest", response_model=SuggestionOut, tags=["drive"])
def suggest(
    request: Request,
    subject_id: str = Query(DEFAULT_SUBJECT_ID, alias="subjectId"),
    vehicle_id: str = Query(DEFAULT_VEHICLE_ID, alias="vehicleId"),
) -> SuggestionOut:
    state = get_trip_service(request, subject_id, vehicle_id).state
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


@router.post("/api/drive/food", tags=["drive"])
def food(
    request: Request,
    payload: Optional[LocationIn] = Body(default=None),
    subject_id: str = Query(DEFAULT_SUBJECT_ID, alias="subjectId"),
    vehicle_id: str = Query(DEFAULT_VEHICLE_ID, alias="vehicleId"),
    response_mode: ResponseMode = Query(ResponseMode.JSON, alias="responseMode"),
) -> Response:
    intent_out = build_intent_response(
        get_intent_service(request, payload, subject_id, vehicle_id),
        DriveIntent.FOOD,
    )
    return render_intent_response(intent_out, response_mode)


@router.post("/api/drive/parking", tags=["drive"])
def parking(
    request: Request,
    payload: Optional[LocationIn] = Body(default=None),
    subject_id: str = Query(DEFAULT_SUBJECT_ID, alias="subjectId"),
    vehicle_id: str = Query(DEFAULT_VEHICLE_ID, alias="vehicleId"),
    response_mode: ResponseMode = Query(ResponseMode.JSON, alias="responseMode"),
) -> Response:
    intent_out = build_intent_response(
        get_intent_service(request, payload, subject_id, vehicle_id),
        DriveIntent.PARKING,
    )
    return render_intent_response(intent_out, response_mode)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Hermes Drive",
        version="0.1.0",
        description="Vehicle trip context and GPS/location ingest service for Hermes.",
    )
    app.state.drive_store = InMemoryDriveStore()
    app.include_router(router)
    return app
