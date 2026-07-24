"""予約に関するドメインモデル(09のエンティティ)。HTTPやDBには依存しない。"""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from uuid import UUID


class ReservationStatus(str, Enum):
    RESERVED = "RESERVED"
    CHECKED_IN = "CHECKED_IN"
    CHECKED_OUT = "CHECKED_OUT"
    CANCELLED = "CANCELLED"


@dataclass(frozen=True)
class Guest:
    name: str
    contact: str


@dataclass(frozen=True)
class Room:
    room_number: str
    room_type: str


@dataclass(frozen=True)
class Reservation:
    id: UUID
    check_in_date: date
    check_out_date: date
    status: ReservationStatus
    guest: Guest
    room: Room
