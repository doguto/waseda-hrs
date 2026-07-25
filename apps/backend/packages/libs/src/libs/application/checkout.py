"""UC3 チェックアウトする のコントロール(BCEのcontrol)。
料金を計算し、請求を発行・支払い記録し、予約と客室の状態を更新する一連を
engine.begin()(コミット付き)の単一トランザクションで実行する。
料金計算そのものはドメイン(billing)に委ね、controlは手順の制御に徹する。"""

from dataclasses import dataclass
from datetime import date
from uuid import UUID

import sqlalchemy

from libs.domain.billing import (
    Charge,
    RoomRateNotConfigured,
    calculate_amount,
)
from libs.domain.reservation import Reservation, ReservationNotFound, RoomStatus
from libs.infrastructure.db.repositories.billing import BillingRepository
from libs.infrastructure.db.repositories.reservation import ReservationRepository


@dataclass(frozen=True)
class CheckOutResult:
    reservation: Reservation
    charge: Charge


class CheckOutControl:
    def __init__(self, engine: sqlalchemy.Engine) -> None:
        self._engine = engine

    def check_out(self, reservation_id: UUID) -> CheckOutResult:
        with self._engine.begin() as conn:
            reservations = ReservationRepository(conn)
            billing = BillingRepository(conn)

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
