"""UC3 チェックアウトする のコントロール(BCEのcontrol)。
料金を計算し、請求を発行・支払い記録し、予約と客室の状態を更新する一連を
UnitOfWork.begin()(コミット付き)の単一トランザクションで実行する。
料金計算そのものはドメイン(billing)に委ね、controlは手順の制御に徹する。"""

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from libs.domain.billing import (
    Charge,
    RoomRateNotConfigured,
    calculate_amount,
)
from libs.domain.repositories import UnitOfWork
from libs.domain.reservation import Reservation, ReservationNotFound, RoomStatus


@dataclass(frozen=True)
class CheckOutResult:
    reservation: Reservation
    charge: Charge


class CheckOutControl:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def check_out(self, reservation_id: UUID) -> CheckOutResult:
        with self._uow.begin() as repositories:
            reservations = repositories.reservations
            billing = repositories.billing

            reservation = reservations.lock_by_id(reservation_id)
            if reservation is None:
                raise ReservationNotFound(str(reservation_id))
            checked_out = reservation.check_out()

            room_rate = billing.find_room_rate(reservation.room.room_type)
            if room_rate is None:
                raise RoomRateNotConfigured(reservation.room.room_type)
            amount = calculate_amount(
                room_rate,
                reservation.nights(),
                billing.list_service_usages(reservation_id),
            )

            issued_date = date.today()
            billing.create_paid_charge(
                reservation_id=reservation_id, amount=amount, issued_date=issued_date
            )
            reservations.set_status(checked_out.id, checked_out.status)
            reservations.set_room_status(
                reservation.room.room_number, RoomStatus.VACANT
            )

            charge = Charge(amount=amount, issued_date=issued_date, paid=True)
            return CheckOutResult(reservation=checked_out, charge=charge)
