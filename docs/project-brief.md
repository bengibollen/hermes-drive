# Hermes Drive — Codex Project Brief

## Purpose

Create a new backend project called `hermes-drive`.

Hermes Drive is **not** a navigation system. It is a backend/service for vehicle trip context, GPS/location ingest, Raspberry Pi telemetry, and travel-assistant features used by Hermes.

The initial real-world setup is:

- A Raspberry Pi 3B+ in a car
- The Pi is connected through Tailscale
- A GPS module will later be attached to the Pi
- Hermes server/agent should be able to know the current vehicle location and trip context
- A phone/web UI may later be used for interaction, voice, maps, and suggestions

The project should start backend-first. Do not start by building a fancy map UI.

## Core idea

The Raspberry Pi should eventually act as the always-on car node:

- GPS logger
- current location publisher
- trip/drive state source
- possible GPIO push-to-talk input later
- possible audio input/output bridge later
- local cache/buffer if network is unavailable

The Hermes/server side should act as the brain:

- receive location and telemetry
- store latest state
- track trips, stops, and driving time
- expose context to Hermes/agents
- later provide stop suggestions, overnight-stay support, food/rest reminders, and place search

The phone/web UI should be treated as a presentation/control layer, not as the core system.

## Main design principle

Build this as **device telemetry + trip context**, not navigation.

Avoid route planning, turn-by-turn navigation, ABRP replacement functionality, and map-heavy UX in the first version.

Good initial scope:

- receive location updates
- store latest vehicle state
- track a trip session
- infer moving/stopped state
- expose API endpoints
- support a simulator while GPS hardware is not ready

Out of scope for now:

- turn-by-turn navigation
- full map dashboard
- OBD integration
- ABRP integration
- voice input/output
- booking automation
- campsite/Google/OSM integrations
- complex agent workflows

## Suggested technology

~~Assume a C#/.NET backend unless the existing workspace clearly indicates otherwise.~~  
Use Python with FastAPI for the initial backend unless there is already a stronger project convention. Keep the code simple, typed where practical, and testable.

Prefer:

- .NET 8 or newer
- ASP.NET Core Minimal API or normal Web API
- simple clean architecture, but do not over-engineer
- SQLite for local development persistence, or in-memory persistence for the very first skeleton if simpler
- Entity Framework Core if persistence is added immediately
- OpenAPI/Swagger enabled for local testing
- basic tests for domain/trip-state logic

The first version should be easy to run locally.

## Suggested repo structure

A simple structure is preferred initially:

```text
hermes-drive/
  README.md
  docs/
    architecture.md
    api.md
    trip-model.md
  src/
    Hermes.Drive.Api/
  tests/
    Hermes.Drive.Tests/
```

Do not create many microservices or excessive projects unless there is a clear reason.

If using a more layered .NET solution, this is acceptable:

```text
src/
  Hermes.Drive.Api/
  Hermes.Drive.Application/
  Hermes.Drive.Domain/
  Hermes.Drive.Infrastructure/
tests/
  Hermes.Drive.Tests/
```

But prefer keeping the first implementation understandable and small.

## Initial domain concepts

### VehicleLocation

Represents one location update from the Pi, simulator, phone, or future OBD/GPS source.

Suggested fields:

```csharp
public sealed record VehicleLocation(
    string DeviceId,
    DateTimeOffset Timestamp,
    double Latitude,
    double Longitude,
    double? SpeedKmh,
    double? Heading,
    double? AccuracyMeters,
    string Source);
```

### TripState

Represents the current known state of a trip.

Suggested fields:

- active trip id
- device id
- latest location
- trip started at
- last movement time
- last stop time
- currently moving/stopped/unknown
- accumulated driving duration
- accumulated stopped duration
- latest update timestamp

### TripSession

Represents a persisted trip/logging session.

Suggested fields:

- id
- device id
- started at
- ended at nullable
- status: active/completed
- optional notes/name

### StopEvent

Represents inferred or manual stops.

Suggested fields:

- trip id
- started at
- ended at nullable
- location
- reason/type nullable
- source: inferred/manual

## Initial API

Start with a small API surface.

### POST /api/drive/location

Receives a location update.

Example payload:

```json
{
  "deviceId": "car-pi",
  "timestamp": "2026-06-07T14:20:00Z",
  "lat": 57.7089,
  "lon": 11.9746,
  "speedKmh": 82,
  "heading": 142,
  "accuracyMeters": 8,
  "source": "simulated"
}
```

Expected behavior:

- validate latitude/longitude
- accept nullable speed/heading/accuracy
- store the latest location
- update current trip state
- infer moving/stopped state in a simple way
- return current trip state or acknowledgement

### GET /api/drive/state

Returns the current trip/vehicle state.

Should work even before real GPS exists.

### POST /api/drive/trips/start

Starts a new trip session.

Initial behavior can be simple:

- create trip id
- mark it active
- associate with device id

### POST /api/drive/trips/stop

Ends the active trip session.

### POST /api/drive/suggest

Placeholder endpoint for future Hermes suggestions.

For the first version this can return a simple deterministic response based on current state, such as:

- no active trip
- no recent location
- has been moving for X minutes
- stopped recently
- later this will call Hermes/agent/place providers

Do not implement real Google/OSM/place search in the first backend skeleton.

## Moving/stopped inference

Keep the first algorithm intentionally simple.

Example rules:

- if no speed is present, state is unknown unless later location deltas can infer movement
- if `speedKmh >= 5`, state is moving
- if `speedKmh < 5`, state is stopped
- later this can be improved with GPS distance over time and smoothing

The logic should live somewhere testable, not directly inside endpoint code.

## Simulator

Because the GPS module is not available yet, create a simulator or test client.

Preferred simple options:

1. A small console app/script that posts fake location updates to `/api/drive/location`
2. A development-only endpoint that generates fake movement
3. A sample `.http` file for manual testing from IDE/VS Code

The simulator should make it possible to test:

- first location received
- moving state
- stopped state
- trip duration
- latest state endpoint

## Persistence

A very first version can use in-memory storage if that gets the skeleton working quickly.

However, design so it can later persist:

- trip sessions
- location logs
- stop events
- latest state

SQLite is fine for local development. PostgreSQL may be used later if Hermes Drive becomes part of a larger deployed backend.

Do not block initial progress on perfect database design.

## Security / network assumptions

The Pi and server are expected to communicate over Tailscale initially.

Still, the API should be designed as if it will later need authentication.

For first skeleton:

- no public exposure required
- local/dev only is fine
- optionally add a simple API key header, but do not overcomplicate auth yet

Suggested future header:

```http
X-Hermes-Device-Key: <secret>
```

## Later features, not first version

These should be noted but not implemented initially:

### Drive Mode UI

Later, Hermes may have a Drive Mode web page showing:

- current location
- last update time
- trip duration
- moving/stopped state
- suggestions
- manual buttons like “I’m hungry”, “find overnight”, “find parking”
- possibly push-to-talk

This may be added to an existing Hermes WebUI later, but should not define the backend shape too early.

### Place providers

Later create an abstraction like:

```csharp
public interface IPlaceProvider
{
    Task<IReadOnlyList<PlaceCandidate>> SearchNearbyAsync(
        GeoPoint location,
        PlaceSearchIntent intent,
        int radiusMeters,
        CancellationToken cancellationToken);
}
```

Possible providers:

- Google Places
- OSM/Overpass
- manual/browser-assisted Park4Night style workflow
- ABRP/charging-related data later

Do not implement this yet.

### OBD

OBD dongle support may later add:

- battery/fuel level
- consumption
- charging/fuel stop prediction
- odometer
- car on/off state
- 12V voltage
- fault codes

Design location/vehicle state with nullable fields so OBD can fill them later, but do not implement OBD now.

### Voice / push-to-talk

Later options:

- phone web UI sends microphone audio to server
- Pi GPIO button triggers recording
- Pi records audio and sends to Hermes
- Hermes response plays through Pi speaker/car audio

Do not implement audio in the first backend skeleton.

## Development plan

### Milestone 1 — Skeleton

Create:

- solution/project structure
- README
- Swagger/OpenAPI
- health endpoint
- basic run instructions

Suggested endpoint:

```http
GET /health
```

### Milestone 2 — Location ingest

Create:

- location DTO
- validation
- POST `/api/drive/location`
- in-memory latest location store
- GET `/api/drive/state`

### Milestone 3 — Trip state

Create:

- trip session model
- start/stop trip endpoints
- current trip state
- simple moving/stopped inference
- basic tests for state transitions

### Milestone 4 — Simulator/test data

Create one of:

- sample `.http` file
- small console simulator
- script to post fake GPS data

This should allow development before the physical GPS module arrives.

### Milestone 5 — Persistence

Add persistence only after the domain and API shape feel reasonable.

Persist:

- trip sessions
- location updates
- stop events
- latest state if useful

### Milestone 6 — Hermes integration

Expose a clean endpoint or internal client so Hermes can ask:

- where is the vehicle?
- how long has it been moving?
- when was the last stop?
- is a suggestion appropriate?
- what is the current trip context?

## Important constraints

- Keep the first version boring and reliable.
- Prefer simple backend primitives over UI-first design.
- Do not build a navigation system.
- Do not overbuild microservices.
- Keep hardware-specific logic out of the core backend.
- The backend should not care whether location comes from real Pi GPS, simulator, phone browser, or future OBD source.
- Make the core trip-state logic testable.
- Prefer incremental commits and small working slices.

## First concrete task for Codex

Please bootstrap the `hermes-drive` project.

Create a minimal backend with:

- README
- project/solution files
- health endpoint
- POST `/api/drive/location`
- GET `/api/drive/state`
- simple in-memory storage
- simple moving/stopped inference based on speed
- Swagger/OpenAPI
- one sample request file or simulator for fake GPS data
- a few tests for the trip-state/movement logic

Keep the implementation simple and easy to change.
