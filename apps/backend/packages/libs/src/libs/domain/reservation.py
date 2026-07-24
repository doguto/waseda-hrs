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


class InvalidReservationPeriod(Exception):
    """宿泊期間が不正なときに送出する(チェックアウトがチェックイン以前など)。"""


class NoAvailableRoom(Exception):
    """指定タイプの空室が無いときに送出する。"""


def ensure_reservable_period(check_in_date: date, check_out_date: date) -> None:
    """宿泊期間の妥当性を検査する。チェックアウトはチェックインより後でなければならない。"""
    if check_out_date <= check_in_date:
        raise InvalidReservationPeriod(
            f"check_out_date {check_out_date} must be after "
            f"check_in_date {check_in_date}"
        )


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

    def check_in(self) -> "Reservation":
        """チェックインする(09の Reservation.チェックインする())。
        チェックインできるのは RESERVED の予約だけ。"""
        if self.status is not ReservationStatus.RESERVED:
            raise InvalidReservationState(
                f"reservation in status {self.status.value} cannot be checked in"
            )
        return replace(self, status=ReservationStatus.CHECKED_IN)

    def check_out(self) -> "Reservation":
        """チェックアウトする(09の Reservation.チェックアウトする())。
        チェックアウトできるのは CHECKED_IN の予約だけ。"""
        if self.status is not ReservationStatus.CHECKED_IN:
            raise InvalidReservationState(
                f"reservation in status {self.status.value} cannot be checked out"
            )
        return replace(self, status=ReservationStatus.CHECKED_OUT)

    def nights(self) -> int:
        """泊数 = チェックアウト日 - チェックイン日。"""
        return (self.check_out_date - self.check_in_date).days

    def cancel(self) -> "Reservation":
        """予約をキャンセルする(09の Reservation.キャンセルする())。
        キャンセルできるのは RESERVED の予約だけ。"""
        if self.status is not ReservationStatus.RESERVED:
            raise InvalidReservationState(
                f"reservation in status {self.status.value} cannot be cancelled"
            )
        return replace(self, status=ReservationStatus.CANCELLED)
