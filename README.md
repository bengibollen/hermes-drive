# Hermes Drive

Backend/service for vehicle trip context, GPS/location ingest, trip state, and
travel-assistant features used by Hermes.

Hermes Drive is not a navigation system. It starts as a small FastAPI service
for receiving vehicle telemetry and exposing current trip context.

## Current Scope

- Receive location updates from Raspberry Pi, simulator, or another source
- Store latest vehicle position in memory
- Track active trip state by subject and vehicle
- Infer moving/stopped/unknown from speed
- Provide API endpoints for Hermes and development clients
- Include a simulator while GPS hardware is not ready

## Requirements

- Python 3.9+

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

## Run

```bash
uvicorn hermes_drive.main:app --reload
```

Then open:

- API docs: <http://127.0.0.1:8000/docs>
- Health: <http://127.0.0.1:8000/health>

## Test

```bash
pytest
```

## Simulate GPS

Start the API, then run:

```bash
python scripts/simulate_gps.py
```

Manual API examples are available in `samples/drive-api.http`.

## Docs

- `docs/project-brief.md`
- `docs/architecture.md`
- `docs/api.md`
- `docs/trip-model.md`
