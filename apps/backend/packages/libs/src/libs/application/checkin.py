"""UC2 チェックインする のコントロール(BCEのcontrol)。
UC5(キャンセル)と同じく engine.begin() でトランザクション境界を張り、
予約と客室の行を lock_by_id でロックしてから状態を書き換える。
状態遷移の可否はエンティティの check_in() が守る。"""

from uuid import UUID

import sqlalchemy

from libs.domain.reservation import Reservation, ReservationNotFound, RoomStatus
from libs.infrastructure.db.repositories.reservation import ReservationRepository


class CheckInControl:
    def __init__(self, engine: sqlalchemy.Engine) -> None:
        self._engine = engine

    def check_in(self, reservation_id: UUID) -> Reservation:
        with self._engine.begin() as conn:
            repository = ReservationRepository(conn)
            reservation = repository.lock_by_id(reservation_id)
            if reservation is None:
                raise ReservationNotFound(str(reservation_id))
            checked_in = reservation.check_in()
            repository.set_status(checked_in.id, checked_in.status)
            repository.set_room_status(checked_in.room.room_number, RoomStatus.OCCUPIED)
            return checked_in
