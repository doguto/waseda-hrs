"""UC5 予約をキャンセルする のコントロール(BCEのcontrol)。
Application層がトランザクション境界となり、書き込みは UnitOfWork.begin()
(コミット付き)で包む。予約と客室の行は lock_by_id でロックしてから状態を書き換える。"""

from uuid import UUID

from libs.domain.repositories import UnitOfWork
from libs.domain.reservation import Reservation, ReservationNotFound, RoomStatus


class CancellationControl:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def cancel_reservation(self, reservation_id: UUID) -> Reservation:
        with self._uow.begin() as repositories:
            reservations = repositories.reservations
            reservation = reservations.lock_by_id(reservation_id)
            if reservation is None:
                raise ReservationNotFound(str(reservation_id))
            cancelled = reservation.cancel()
            reservations.set_status(cancelled.id, cancelled.status)
            reservations.set_room_status(cancelled.room.room_number, RoomStatus.VACANT)
            return cancelled
