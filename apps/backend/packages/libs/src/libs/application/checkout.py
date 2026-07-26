"""UC3 チェックアウトする のコントロール(BCEのcontrol)。
料金の計算・未払い請求の発行と、支払い記録・チェックアウト完了を分離する。
支払いが行われない場合は予約をCHECKED_INのまま維持する。"""

from dataclasses import dataclass
from datetime import date
from uuid import UUID

import sqlalchemy

from libs.domain.billing import (
    Charge,
    ChargeNotFound,
    RoomRateNotConfigured,
    calculate_amount,
)
from libs.domain.reservation import (
    Reservation,
    ReservationNotFound,
    ReservationStatus,
    RoomStatus,
)
from libs.infrastructure.db.repositories.billing import BillingRepository
from libs.infrastructure.db.repositories.reservation import ReservationRepository


@dataclass(frozen=True)
class CheckOutResult:
    reservation: Reservation
    charge: Charge


class CheckOutControl:
    def __init__(self, engine: sqlalchemy.Engine) -> None:
        self._engine = engine

    def issue_charge(self, reservation_id: UUID) -> CheckOutResult:
        with self._engine.begin() as conn:
            reservations = ReservationRepository(conn)
            billing = BillingRepository(conn)

            reservation = reservations.lock_by_id(reservation_id)
            if reservation is None:
                raise ReservationNotFound(str(reservation_id))
            reservation.check_out()

            charge = billing.lock_charge(reservation_id)
            if charge is None:
                room_rate = billing.find_room_rate(reservation.room.room_type)
                if room_rate is None:
                    raise RoomRateNotConfigured(reservation.room.room_type)
                amount = calculate_amount(
                    room_rate,
                    reservation.nights(),
                    billing.list_service_usages(reservation_id),
                )
                charge = billing.create_charge(
                    reservation_id=reservation_id,
                    amount=amount,
                    issued_date=date.today(),
                )

            return CheckOutResult(reservation=reservation, charge=charge)

    def find_charge(self, reservation_id: UUID) -> Charge | None:
        with self._engine.connect() as conn:
            return BillingRepository(conn).find_charge(reservation_id)

    def pay(self, reservation_id: UUID) -> CheckOutResult:
        with self._engine.begin() as conn:
            reservations = ReservationRepository(conn)
            billing = BillingRepository(conn)

            reservation = reservations.lock_by_id(reservation_id)
            if reservation is None:
                raise ReservationNotFound(str(reservation_id))

            charge = billing.lock_charge(reservation_id)
            if (
                reservation.status is ReservationStatus.CHECKED_OUT
                and charge is not None
                and charge.paid
            ):
                return CheckOutResult(reservation=reservation, charge=charge)

            checked_out = reservation.check_out()
            if charge is None:
                raise ChargeNotFound(str(reservation_id))

            paid_charge = billing.mark_charge_paid(reservation_id)
            reservations.set_status(checked_out.id, checked_out.status)
            reservations.set_room_status(
                reservation.room.room_number, RoomStatus.VACANT
            )

            return CheckOutResult(reservation=checked_out, charge=paid_charge)
