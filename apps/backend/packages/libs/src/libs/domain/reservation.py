"""予約に関するドメインモデル(09のエンティティ)。HTTPやDBには依存しない。
状態遷移の可否(不変条件)はエンティティ自身が守り、Control層はオーケストレーション
とトランザクション境界に徹する。"""

from dataclasses import dataclass, replace
from datetime import date
from enum import Enum
from uuid import UUID


class ReservationStatus(str, Enum):
    RESERVED = "RESERVED"
    CHECKED_IN = "CHECKED_IN"
    CHECKED_OUT = "CHECKED_OUT"
    CANCELLED = "CANCELLED"


class RoomStatus(str, Enum):
    VACANT = "VACANT"
    RESERVED = "RESERVED"
    OCCUPIED = "OCCUPIED"


class ReservationNotFound(Exception):
    """指定された予約が存在しないときに送出する。"""


class InvalidReservationState(Exception):
    """予約が現在の状態では要求された遷移を許さないときに送出する。"""


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

    def cancel(self) -> "Reservation":
        """予約をキャンセルする(09の Reservation.キャンセルする())。
        キャンセルできるのは RESERVED の予約だけ。"""
        if self.status is not ReservationStatus.RESERVED:
            raise InvalidReservationState(
                f"reservation in status {self.status.value} cannot be cancelled"
            )
        return replace(self, status=ReservationStatus.CANCELLED)
