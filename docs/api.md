# API

OpenAPI is available at `/docs` when the local server is running.

## Endpoints

### `GET /health`

Returns service health.

### `POST /api/drive/location`

Receives a vehicle location update and returns current trip state.

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

Validation:

- `lat` must be between -90 and 90.
- `lon` must be between -180 and 180.
- `speedKmh`, `heading`, and `accuracyMeters` are optional.
- `heading`, when present, must be at least 0 and below 360.

### `GET /api/drive/state`

Returns the current known vehicle/trip state. This works before any location has
been received.

### `POST /api/drive/trips/start`

Starts a trip session.

```json
{
  "deviceId": "car-pi"
}
```

### `POST /api/drive/trips/stop`

Stops the current active trip session if one exists.

### `POST /api/drive/suggest`

Placeholder endpoint for future Hermes suggestions. It currently returns a
deterministic message based on active trip and movement state.
