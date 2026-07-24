"""UC5 予約をキャンセルする のコントロール(BCEのcontrol)。
Application層がトランザクション境界となり、書き込みは engine.begin()(コミット付き)
で包む。予約と客室の行は lock_by_id でロックしてから状態を書き換える。"""

from uuid import UUID

import sqlalchemy

from libs.domain.reservation import Reservation, ReservationNotFound, RoomStatus
from libs.infrastructure.db.repositories.reservation import ReservationRepository


class CancellationControl:
    def __init__(self, engine: sqlalchemy.Engine) -> None:
        self._engine = engine

    def cancel_reservation(self, reservation_id: UUID) -> Reservation:
        with self._engine.begin() as conn:
            repository = ReservationRepository(conn)
            reservation = repository.lock_by_id(reservation_id)
            if reservation is None:
                raise ReservationNotFound(str(reservation_id))
            cancelled = reservation.cancel()
            repository.set_status(cancelled.id, cancelled.status)
            repository.set_room_status(cancelled.room.room_number, RoomStatus.VACANT)
            return cancelled
