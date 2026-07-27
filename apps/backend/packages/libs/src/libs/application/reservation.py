"""UC1 部屋を予約する のコントロール(BCEのcontrol)。
空室を1つロックして確保し、利用者と予約を登録する一連の手順を
UnitOfWork.begin()(コミット付き)の単一トランザクションで実行する。"""

from datetime import date
from uuid import UUID

from libs.domain.repositories import UnitOfWork
from libs.domain.reservation import (
    Guest,
    NoAvailableRoom,
    Reservation,
    ReservationStatus,
    RoomStatus,
    ensure_reservable_period,
)


class ReservationControl:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def reserve(
        self,
        *,
        room_type: str,
        check_in_date: date,
        check_out_date: date,
        guest_name: str,
        guest_contact: str,
    ) -> Reservation:
        ensure_reservable_period(check_in_date, check_out_date)
        with self._uow.begin() as repositories:
            reservations = repositories.reservations
            room = reservations.find_and_lock_vacant_room(room_type)
            if room is None:
                raise NoAvailableRoom(f"no vacant room for type {room_type}")
            guest = Guest(name=guest_name, contact=guest_contact)
            guest_id: UUID = reservations.create_guest(guest)
            reservation_id = reservations.create_reservation(
                guest_id=guest_id,
                room_number=room.room_number,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
            )
            reservations.set_room_status(room.room_number, RoomStatus.RESERVED)
            return Reservation(
                id=reservation_id,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                status=ReservationStatus.RESERVED,
                guest=guest,
                room=room,
            )
