"""UC3 チェックアウトする のコントロール(BCEのcontrol)。
料金の計算・未払い請求の発行と、支払い記録・チェックアウト完了を分離する。
支払いが行われない場合は予約をCHECKED_INのまま維持する。"""

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from libs.domain.billing import (
    Charge,
    ChargeNotFound,
    RoomRateNotConfigured,
    calculate_amount,
)
from libs.domain.repositories import UnitOfWork
from libs.domain.reservation import (
    Reservation,
    ReservationNotFound,
    ReservationStatus,
    RoomStatus,
)


@dataclass(frozen=True)
class CheckOutResult:
    reservation: Reservation
    charge: Charge


class CheckOutControl:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def issue_charge(self, reservation_id: UUID) -> CheckOutResult:
        with self._uow.begin() as repositories:
            reservations = repositories.reservations
            billing = repositories.billing

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
        with self._uow.read() as repositories:
            return repositories.billing.find_charge(reservation_id)

    def pay(self, reservation_id: UUID) -> CheckOutResult:
        with self._uow.begin() as repositories:
            reservations = repositories.reservations
            billing = repositories.billing

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
