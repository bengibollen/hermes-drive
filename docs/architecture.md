# Architecture

Hermes Drive starts as a small FastAPI backend. It receives vehicle location
updates from a Raspberry Pi, simulator, phone, or future hardware source and
turns them into current trip context for Hermes.

The first implementation is intentionally in-memory. Persistence can be added
behind the storage boundary once the domain model and API shape settle.

## Structure

```text
src/hermes_drive/
  api/        FastAPI app, request/response schemas, route handlers
  domain/     Vehicle location, trip state, movement inference
  storage/    In-memory service holder for the first version
scripts/      Development simulator/client scripts
samples/      Manual API request examples
tests/        Unit and API tests
```

## Current Flow

1. A client posts a location update to `POST /api/drive/location`.
2. Pydantic validates the payload and converts it to a domain model.
3. The in-memory store chooses a trip context by `subjectId` and `vehicleId`.
4. `TripService` infers movement from speed:
   - no speed: `unknown`
   - speed below 5 km/h: `stopped`
   - speed at or above 5 km/h: `moving`
5. The current state is updated in memory.
6. The API returns the current trip state.

## Non-Goals For This Slice

- Turn-by-turn navigation
- Map UI
- OBD integration
- Place search
- Voice or push-to-talk
- Durable persistence
