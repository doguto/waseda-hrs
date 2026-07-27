"""UC2 チェックインする のコントロールに対するテスト。

状態遷移の可否そのものはエンティティのテストで網羅済みなので、ここでは
「Control が予約と客室の両方を正しく更新するか」
「失敗時に副作用が残らないか」を確認する。
"""

from uuid import uuid4

import pytest
from libs.application.checkin import CheckInControl
from libs.domain.reservation import (
    InvalidReservationState,
    ReservationNotFound,
    ReservationStatus,
    RoomStatus,
)

from tests.application.conftest import add_reservation
from tests.application.fakes import FakeDatabase, FakeUnitOfWork


class TestCheckIn:
    def test_updates_reservation_and_room(
        self, uow: FakeUnitOfWork, db: FakeDatabase
    ) -> None:
        """基本フロー: 予約はチェックイン済み、客室は使用中になる。"""
        reservation_id = add_reservation(db, status=ReservationStatus.RESERVED)

        checked_in = CheckInControl(uow).check_in(reservation_id)

        assert checked_in.status is ReservationStatus.CHECKED_IN
        assert (
            uow.db.reservations[reservation_id].status is ReservationStatus.CHECKED_IN
        )
        assert uow.db.rooms["101"].status is RoomStatus.OCCUPIED
        assert uow.commits == 1

    def test_locks_the_reservation_before_updating(
        self, uow: FakeUnitOfWork, db: FakeDatabase
    ) -> None:
        """更新前提の読み取りなので、ロック付きで取得する。"""
        reservation_id = add_reservation(db, status=ReservationStatus.RESERVED)

        CheckInControl(uow).check_in(reservation_id)

        assert uow.db.locked_reservation_ids == [reservation_id]

    def test_raises_when_reservation_is_missing(self, uow: FakeUnitOfWork) -> None:
        """例外フロー3a: 該当予約が無ければ ReservationNotFound。"""
        with pytest.raises(ReservationNotFound):
            CheckInControl(uow).check_in(uuid4())

        assert uow.rollbacks == 1

    @pytest.mark.parametrize(
        "status",
        [
            ReservationStatus.CHECKED_IN,
            ReservationStatus.CHECKED_OUT,
            ReservationStatus.CANCELLED,
        ],
    )
    def test_rejects_invalid_state_without_side_effects(
        self, uow: FakeUnitOfWork, db: FakeDatabase, status: ReservationStatus
    ) -> None:
        """遷移できない状態なら、客室の状態も書き換わらない(ロールバック)。"""
        reservation_id = add_reservation(db, status=status)
        room_status_before = db.rooms["101"].status

        with pytest.raises(InvalidReservationState):
            CheckInControl(uow).check_in(reservation_id)

        assert uow.db.reservations[reservation_id].status is status
        assert uow.db.rooms["101"].status is room_status_before
        assert uow.commits == 0
        assert uow.rollbacks == 1
