"""UC5 予約をキャンセルする のコントロールに対するテスト。"""

from uuid import uuid4

import pytest
from libs.application.cancellation import CancellationControl
from libs.domain.reservation import (
    InvalidReservationState,
    ReservationNotFound,
    ReservationStatus,
    RoomStatus,
)

from tests.application.conftest import add_reservation
from tests.application.fakes import FakeDatabase, FakeUnitOfWork


class TestCancelReservation:
    def test_cancels_and_frees_the_room(
        self, uow: FakeUnitOfWork, db: FakeDatabase
    ) -> None:
        """基本フロー: 予約はキャンセル済み、客室は空室に戻る。"""
        reservation_id = add_reservation(db, status=ReservationStatus.RESERVED)

        cancelled = CancellationControl(uow).cancel_reservation(reservation_id)

        assert cancelled.status is ReservationStatus.CANCELLED
        assert uow.db.reservations[reservation_id].status is ReservationStatus.CANCELLED
        assert uow.db.rooms["101"].status is RoomStatus.VACANT
        assert uow.commits == 1

    def test_raises_when_reservation_is_missing(self, uow: FakeUnitOfWork) -> None:
        """例外フロー3a: 該当予約が無ければ ReservationNotFound。"""
        with pytest.raises(ReservationNotFound):
            CancellationControl(uow).cancel_reservation(uuid4())

    @pytest.mark.parametrize(
        "status",
        [
            ReservationStatus.CHECKED_IN,
            ReservationStatus.CHECKED_OUT,
            ReservationStatus.CANCELLED,
        ],
    )
    def test_rejects_invalid_state_and_keeps_the_room(
        self, uow: FakeUnitOfWork, db: FakeDatabase, status: ReservationStatus
    ) -> None:
        """例外フロー4a: キャンセル不可の状態では客室も解放しない。"""
        reservation_id = add_reservation(db, status=status)
        room_status_before = db.rooms["101"].status

        with pytest.raises(InvalidReservationState):
            CancellationControl(uow).cancel_reservation(reservation_id)

        assert uow.db.reservations[reservation_id].status is status
        assert uow.db.rooms["101"].status is room_status_before
        assert uow.rollbacks == 1

    def test_cancelled_room_becomes_reservable_again(
        self, uow: FakeUnitOfWork, db: FakeDatabase
    ) -> None:
        """キャンセルで空室に戻った客室は、再び空室として見える。"""
        reservation_id = add_reservation(db, status=ReservationStatus.RESERVED)

        CancellationControl(uow).cancel_reservation(reservation_id)

        vacant = [
            r.room_number
            for r in uow.db.rooms.values()
            if r.status is RoomStatus.VACANT
        ]
        assert "101" in vacant
