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
  "subjectId": "default",
  "vehicleId": "default",
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

- `deviceId` is required.
- `subjectId` is optional and defaults to `default`.
- `vehicleId` is optional and defaults to `default`.
- `lat` must be between -90 and 90.
- `lon` must be between -180 and 180.
- `speedKmh`, `heading`, and `accuracyMeters` are optional.
- `heading`, when present, must be at least 0 and below 360.

### `GET /api/drive/state`

Returns the current known vehicle/trip state. This works before any location has
been received.

Optional query parameters:

- `subjectId`, default `default`
- `vehicleId`, default `default`

### `POST /api/drive/trips/start`

Starts a trip session.

```json
{
  "deviceId": "car-pi",
  "subjectId": "default",
  "vehicleId": "default"
}
```

### `POST /api/drive/trips/stop`

Stops the current active trip session if one exists.

Optional query parameters:

- `subjectId`, default `default`
- `vehicleId`, default `default`

### `POST /api/drive/suggest`

Placeholder endpoint for future Hermes suggestions. It currently returns a
deterministic message based on active trip and movement state.

Optional query parameters:

- `subjectId`, default `default`
- `vehicleId`, default `default`

### `POST /api/drive/food`

Records that the user is hungry and returns a deterministic response for the
client. This does not perform real place search yet.

The request body is optional. If present, it uses the same shape as
`POST /api/drive/location` and is ingested before the food response is built.
This lets a Pi button press send current position and direction in one call.

Optional query parameters:

- `subjectId`, default `default`
- `vehicleId`, default `default`
- `responseMode`, default `json`

Supported `responseMode` values:

- `json`: returns structured JSON.
- `text`: returns `text/plain`.
- `speech`: reserved for future speech output and currently returns `501 Not Implemented`.

Example:

```http
POST /api/drive/food?subjectId=danne&vehicleId=car&responseMode=json
```

Example with current position:

```json
{
  "deviceId": "car-pi",
  "subjectId": "danne",
  "vehicleId": "car",
  "timestamp": "2026-06-07T14:20:00Z",
  "lat": 57.7089,
  "lon": 11.9746,
  "speedKmh": 82,
  "heading": 142,
  "accuracyMeters": 8,
  "source": "gpsd"
}
```

### `POST /api/drive/parking`

Records that the user needs parking or a rest stop and returns a deterministic
response for the client. This does not perform real place search yet.

The request body is optional. If present, it uses the same shape as
`POST /api/drive/location` and is ingested before the parking/rest response is
built. This lets a Pi button press send current position and direction in one
call.

Optional query parameters:

- `subjectId`, default `default`
- `vehicleId`, default `default`
- `responseMode`, default `json`

Supported `responseMode` values:

- `json`: returns structured JSON.
- `text`: returns `text/plain`.
- `speech`: reserved for future speech output and currently returns `501 Not Implemented`.

Example:

```http
POST /api/drive/parking?subjectId=danne&vehicleId=car&responseMode=text
```
