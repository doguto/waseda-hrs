"""予約のDBアクセスadapter。sqlc生成コードをドメインモデルに変換し、
Application層がsqlcへ直接依存しないようにする。"""

from uuid import UUID

import sqlalchemy

from libs.domain.reservation import Guest, Reservation, ReservationStatus, Room
from libs.infrastructure.db.gen.reservation import Querier


class ReservationRepository:
    def __init__(self, conn: sqlalchemy.engine.Connection) -> None:
        self._querier = Querier(conn)

    def find_by_id(self, reservation_id: UUID) -> Reservation | None:
        row = self._querier.get_reservation_by_id(id=reservation_id)
        if row is None:
            return None
        return Reservation(
            id=row.id,
            check_in_date=row.check_in_date,
            check_out_date=row.check_out_date,
            status=ReservationStatus(row.status.value),
            guest=Guest(name=row.guest_name, contact=row.guest_contact),
            room=Room(room_number=row.room_number, room_type=row.room_type),
        )
