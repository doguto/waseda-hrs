"""UC4 予約内容を確認する のコントロール(BCEのcontrol)。
Application層がトランザクション境界となり、接続の開閉を受け持つ。"""

from uuid import UUID

import sqlalchemy

from libs.domain.reservation import Reservation
from libs.infrastructure.db.repositories.reservation import ReservationRepository


class InquiryControl:
    def __init__(self, engine: sqlalchemy.Engine) -> None:
        self._engine = engine

    def find_reservation(self, reservation_id: UUID) -> Reservation | None:
        with self._engine.connect() as conn:
            repository = ReservationRepository(conn)
            return repository.find_by_id(reservation_id)
