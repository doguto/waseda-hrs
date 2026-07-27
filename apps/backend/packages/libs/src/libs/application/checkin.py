"""UC2 チェックインする のコントロール(BCEのcontrol)。
UC5(キャンセル)と同じく UnitOfWork.begin() でトランザクション境界を張り、
予約と客室の行を lock_by_id でロックしてから状態を書き換える。
状態遷移の可否はエンティティの check_in() が守る。"""

from uuid import UUID

from libs.domain.repositories import UnitOfWork
from libs.domain.reservation import Reservation, ReservationNotFound, RoomStatus


class CheckInControl:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def check_in(self, reservation_id: UUID) -> Reservation:
        with self._uow.begin() as repositories:
            reservations = repositories.reservations
            reservation = reservations.lock_by_id(reservation_id)
            if reservation is None:
                raise ReservationNotFound(str(reservation_id))
            checked_in = reservation.check_in()
            reservations.set_status(checked_in.id, checked_in.status)
            reservations.set_room_status(
                checked_in.room.room_number, RoomStatus.OCCUPIED
            )
            return checked_in
