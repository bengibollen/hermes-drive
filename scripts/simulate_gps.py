from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone

import httpx


def build_payload(index: int) -> dict[str, object]:
    speed_kmh = 72 if index < 6 else 0
    return {
        "deviceId": "car-pi",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "lat": 57.7089 + index * 0.001,
        "lon": 11.9746 + index * 0.001,
        "speedKmh": speed_kmh,
        "heading": 142,
        "accuracyMeters": 8,
        "source": "simulated",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Post fake GPS updates to Hermes Drive.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--count", type=int, default=10)
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()

    with httpx.Client(base_url=args.base_url, timeout=10) as client:
        for index in range(args.count):
            response = client.post("/api/drive/location", json=build_payload(index))
            response.raise_for_status()
            state = response.json()
            print(
                f"{index + 1}/{args.count}: "
                f"{state['movementStatus']} at {state['latestLocation']['lat']},"
                f"{state['latestLocation']['lon']}"
            )
            time.sleep(args.interval)


if __name__ == "__main__":
    main()
