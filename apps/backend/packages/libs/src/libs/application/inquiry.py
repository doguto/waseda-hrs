"""UC4 予約内容を確認する のコントロール(BCEのcontrol)。
Application層がトランザクション境界となり、接続の開閉は UnitOfWork に委ねる。"""

from uuid import UUID

from libs.domain.repositories import UnitOfWork
from libs.domain.reservation import Reservation


class InquiryControl:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def find_reservation(self, reservation_id: UUID) -> Reservation | None:
        with self._uow.read() as repositories:
            return repositories.reservations.find_by_id(reservation_id)
