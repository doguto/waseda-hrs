"""UC4 予約内容を確認する のコントロールに対するテスト。

参照のみのユースケースなので、書き込み用のトランザクションを開かないこと
（`read()` を使うこと）も確認する。
"""

from uuid import uuid4

from libs.application.inquiry import InquiryControl
from libs.domain.reservation import ReservationStatus

from tests.application.conftest import CHECK_IN_DATE, CHECK_OUT_DATE, add_reservation
from tests.application.fakes import FakeDatabase, FakeUnitOfWork


class TestFindReservation:
    def test_returns_reservation_with_guest_and_room(
        self, uow: FakeUnitOfWork, db: FakeDatabase
    ) -> None:
        """基本フロー: 宿泊日・客室・予約状態を伴って返る。"""
        reservation_id = add_reservation(db, status=ReservationStatus.RESERVED)

        reservation = InquiryControl(uow).find_reservation(reservation_id)

        assert reservation is not None
        assert reservation.id == reservation_id
        assert reservation.check_in_date == CHECK_IN_DATE
        assert reservation.check_out_date == CHECK_OUT_DATE
        assert reservation.status is ReservationStatus.RESERVED
        assert reservation.guest.name == "山田太郎"
        assert reservation.room.room_number == "101"

    def test_returns_none_when_missing(self, uow: FakeUnitOfWork) -> None:
        """例外フロー2a: 該当が無ければ None（UI層で404に変換される）。"""
        assert InquiryControl(uow).find_reservation(uuid4()) is None

    def test_uses_read_only_transaction(
        self, uow: FakeUnitOfWork, db: FakeDatabase
    ) -> None:
        """照会は状態を変えないので、書き込み用トランザクションを開かない。"""
        reservation_id = add_reservation(db, status=ReservationStatus.RESERVED)

        InquiryControl(uow).find_reservation(reservation_id)

        assert uow.reads == 1
        assert uow.commits == 0
        assert uow.db.locked_reservation_ids == []
