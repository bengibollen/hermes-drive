# Trip Model

## VehicleLocation

One location update from a Pi, simulator, phone, GPS module, or future vehicle
source.

Fields:

- `device_id`
- `timestamp`
- `latitude`
- `longitude`
- `speed_kmh`
- `heading`
- `accuracy_meters`
- `source`

## TripState

The current known state for the vehicle and active trip.

Fields:

- `device_id`
- `active_trip_id`
- `latest_location`
- `trip_started_at`
- `last_movement_at`
- `last_stop_at`
- `movement_status`
- `accumulated_driving_seconds`
- `accumulated_stopped_seconds`
- `latest_update_at`

## Movement Inference

The first movement algorithm is deliberately simple:

- no speed: `unknown`
- `speed_kmh < 5`: `stopped`
- `speed_kmh >= 5`: `moving`

Duration accumulation is based on the previous known status. For example, if the
previous update was `moving` and the next update arrives five minutes later, five
minutes are added to driving time.
