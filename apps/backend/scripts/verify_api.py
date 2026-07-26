"""Run a repeatable API smoke test against the local Docker Compose stack."""

from __future__ import annotations

import json
import os
import sys
from datetime import date, timedelta
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE_URL = os.environ.get("HRS_API_URL", "http://localhost:8080").rstrip("/")


def request(
    method: str, path: str, payload: dict[str, Any] | None = None
) -> tuple[int, Any]:
    body = json.dumps(payload).encode() if payload is not None else None
    headers = {"Content-Type": "application/json"} if body is not None else {}
    request_object = Request(
        f"{BASE_URL}{path}", data=body, headers=headers, method=method
    )

    try:
        with urlopen(request_object, timeout=10) as response:
            response_body = response.read().decode()
            return response.status, json.loads(response_body) if response_body else None
    except HTTPError as error:
        response_body = error.read().decode()
        detail = response_body or error.reason
        raise AssertionError(
            f"{method} {path} returned {error.code}: {detail}"
        ) from error
    except URLError as error:
        raise AssertionError(f"could not reach {BASE_URL}: {error.reason}") from error


def expect_status(actual: int, expected: int, path: str) -> None:
    if actual != expected:
        raise AssertionError(f"{path} returned {actual}; expected {expected}")


def reserve(room_type: str, guest_name: str) -> dict[str, Any]:
    check_in_date = date.today() + timedelta(days=7)
    check_out_date = check_in_date + timedelta(days=2)
    status, reservation = request(
        "POST",
        "/reservations",
        {
            "room_type": room_type,
            "check_in_date": check_in_date.isoformat(),
            "check_out_date": check_out_date.isoformat(),
            "guest_name": guest_name,
            "guest_contact": "demo@example.com",
        },
    )
    expect_status(status, 201, "/reservations")
    if reservation["status"] != "RESERVED":
        raise AssertionError("new reservation must be RESERVED")
    return reservation


def main() -> None:
    status, health = request("GET", "/healthz")
    expect_status(status, 200, "/healthz")
    if health != {"status": "ok"}:
        raise AssertionError("health check did not return ok")

    status, room_types = request("GET", "/room-types")
    expect_status(status, 200, "/room-types")
    if not {"standard", "deluxe", "suite"}.issubset(
        {room_type["room_type"] for room_type in room_types}
    ):
        raise AssertionError("demo room types are not available")

    checked_out_reservation = reserve("standard", "Demo Check-out Guest")
    checked_out_id = checked_out_reservation["reservation_id"]

    status, reservation = request("GET", f"/reservations/{checked_out_id}")
    expect_status(status, 200, f"/reservations/{checked_out_id}")
    if reservation["status"] != "RESERVED":
        raise AssertionError("reservation inquiry must return the current status")

    status, reservation = request("POST", f"/reservations/{checked_out_id}/check-in")
    expect_status(status, 200, f"/reservations/{checked_out_id}/check-in")
    if reservation["status"] != "CHECKED_IN":
        raise AssertionError("check-in must update the reservation status")

    status, checked_out = request("POST", f"/reservations/{checked_out_id}/check-out")
    expect_status(status, 200, f"/reservations/{checked_out_id}/check-out")
    if checked_out["reservation"]["status"] != "CHECKED_OUT":
        raise AssertionError("check-out must update the reservation status")
    if checked_out["charge"]["amount"] != 20000 or not checked_out["charge"]["paid"]:
        raise AssertionError("check-out must create a paid two-night standard charge")

    cancelled_reservation = reserve("deluxe", "Demo Cancellation Guest")
    cancelled_id = cancelled_reservation["reservation_id"]
    status, reservation = request("POST", f"/reservations/{cancelled_id}/cancellation")
    expect_status(status, 200, f"/reservations/{cancelled_id}/cancellation")
    if reservation["status"] != "CANCELLED":
        raise AssertionError("cancellation must update the reservation status")

    print("API smoke test passed: UC1, UC2, UC3, UC4, and UC5")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as error:
        print(f"API smoke test failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
