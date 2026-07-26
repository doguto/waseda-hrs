"""UC1 部屋を予約する のコントロールに対するテスト。

09のコラボレーション図(08a)が定める手順 —— 空室をロックして確保し、利用者を登録し、
予約を作り、客室を予約済みにする —— を1トランザクションで行うことを確認する。
"""

import pytest
from libs.application.reservation import ReservationControl
from libs.domain.repositories import UnitOfWork
from libs.domain.reservation import (
    InvalidReservationPeriod,
    NoAvailableRoom,
    Reservation,
    ReservationStatus,
    RoomStatus,
)

from tests.application.conftest import CHECK_IN_DATE, CHECK_OUT_DATE
from tests.application.fakes import FakeDatabase, FakeUnitOfWork


def reserve_single(control: ReservationControl) -> Reservation:
    return control.reserve(
        room_type="SINGLE",
        check_in_date=CHECK_IN_DATE,
        check_out_date=CHECK_OUT_DATE,
        guest_name="山田太郎",
        guest_contact="yamada@example.com",
    )


class TestReserve:
    def test_registers_guest_reservation_and_marks_room_reserved(
        self, uow: FakeUnitOfWork, db: FakeDatabase
    ) -> None:
        """基本フロー: 利用者・予約が登録され、確保した客室が予約済みになる。"""
        reservation = ReservationControl(uow).reserve(
            room_type="SINGLE",
            check_in_date=CHECK_IN_DATE,
            check_out_date=CHECK_OUT_DATE,
            guest_name="山田太郎",
            guest_contact="yamada@example.com",
        )

        assert reservation.status is ReservationStatus.RESERVED
        assert reservation.room.room_type == "SINGLE"
        assert reservation.guest.name == "山田太郎"
        assert len(db.reservations) == 1
        assert len(db.guests) == 1
        assert db.rooms[reservation.room.room_number].status is RoomStatus.RESERVED
        assert uow.commits == 1

    def test_locks_the_room_type_before_reserving(self, uow: FakeUnitOfWork) -> None:
        """UC1の例外フロー(予約の競合)に備え、空室は確保時にロックする。"""
        reserve_single(ReservationControl(uow))

        assert uow.db.locked_room_types == ["SINGLE"]

    def test_rejects_when_no_vacant_room(self, uow: FakeUnitOfWork) -> None:
        """例外フロー2a: 空室が1件も無ければ NoAvailableRoom。"""
        for row in uow.db.rooms.values():
            row.status = RoomStatus.OCCUPIED

        with pytest.raises(NoAvailableRoom):
            reserve_single(ReservationControl(uow))

        assert uow.rollbacks == 1
        assert uow.db.reservations == {}

    def test_rejects_invalid_period_without_opening_transaction(
        self, uow: FakeUnitOfWork
    ) -> None:
        """宿泊期間の検査はトランザクションを開く前に済ませる。"""
        with pytest.raises(InvalidReservationPeriod):
            ReservationControl(uow).reserve(
                room_type="SINGLE",
                check_in_date=CHECK_OUT_DATE,
                check_out_date=CHECK_IN_DATE,
                guest_name="山田太郎",
                guest_contact="yamada@example.com",
            )

        assert uow.commits == 0
        assert uow.rollbacks == 0

    def test_second_reservation_takes_another_room(self, uow: FakeUnitOfWork) -> None:
        """先に確保された客室は再び確保されない。"""
        first = reserve_single(ReservationControl(uow))
        second = reserve_single(ReservationControl(uow))

        assert first.room.room_number != second.room.room_number
        assert uow.db.rooms[first.room.room_number].status is RoomStatus.RESERVED
        assert uow.db.rooms[second.room.room_number].status is RoomStatus.RESERVED

    def test_accepts_any_unit_of_work_port(self, port: UnitOfWork) -> None:
        """Control はポート(Protocol)にのみ依存する。"""
        reservation = ReservationControl(port).reserve(
            room_type="TWIN",
            check_in_date=CHECK_IN_DATE,
            check_out_date=CHECK_OUT_DATE,
            guest_name="鈴木一郎",
            guest_contact="suzuki@example.com",
        )

        assert reservation.room.room_type == "TWIN"
