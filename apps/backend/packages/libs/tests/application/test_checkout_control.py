"""UC3 チェックアウトする のコントロールに対するテスト。

料金計算そのものはドメイン(billing)のテストで確認済み。ここでは Control が
「単価・泊数・追加サービスを集めてドメインに計算させ、請求を支払い済みで記録し、
予約と客室の状態を更新する」一連を1トランザクションで行うことを確認する。
"""

from datetime import date
from uuid import uuid4

import pytest
from libs.application.checkout import CheckOutControl
from libs.domain.billing import RoomRateNotConfigured, ServiceUsage
from libs.domain.reservation import (
    InvalidReservationState,
    ReservationNotFound,
    ReservationStatus,
    RoomStatus,
)

from tests.application.conftest import SINGLE_PRICE, add_reservation
from tests.application.fakes import FakeDatabase, FakeUnitOfWork

THREE_NIGHTS = 3


class TestCheckOut:
    def test_charges_room_only_when_no_services(
        self, uow: FakeUnitOfWork, db: FakeDatabase
    ) -> None:
        """基本フロー: 請求額 = 単価 × 泊数。"""
        reservation_id = add_reservation(db, status=ReservationStatus.CHECKED_IN)

        result = CheckOutControl(uow).check_out(reservation_id)

        assert result.charge.amount == SINGLE_PRICE * THREE_NIGHTS
        assert result.charge.paid is True
        assert result.charge.issued_date == date.today()
        assert result.reservation.status is ReservationStatus.CHECKED_OUT

    def test_adds_service_fees(self, uow: FakeUnitOfWork, db: FakeDatabase) -> None:
        """代替フロー2a: 追加サービスの利用があれば加算する。"""
        reservation_id = add_reservation(
            db,
            status=ReservationStatus.CHECKED_IN,
            services=[
                ServiceUsage(service_name="ルームサービス", fee=3000),
                ServiceUsage(service_name="ランドリー", fee=1200),
            ],
        )

        result = CheckOutControl(uow).check_out(reservation_id)

        assert result.charge.amount == SINGLE_PRICE * THREE_NIGHTS + 4200

    def test_records_paid_charge_and_frees_the_room(
        self, uow: FakeUnitOfWork, db: FakeDatabase
    ) -> None:
        """支払い記録が残り、客室は空室に戻る。"""
        reservation_id = add_reservation(db, status=ReservationStatus.CHECKED_IN)

        CheckOutControl(uow).check_out(reservation_id)

        assert len(uow.db.charges) == 1
        charge = uow.db.charges[0]
        assert charge.reservation_id == reservation_id
        assert charge.paid is True
        assert uow.db.rooms["101"].status is RoomStatus.VACANT
        assert uow.commits == 1

    def test_raises_when_room_rate_is_not_configured(
        self, uow: FakeUnitOfWork, db: FakeDatabase
    ) -> None:
        """料金表が無い客室タイプは請求を作らずに失敗する。"""
        reservation_id = add_reservation(db, status=ReservationStatus.CHECKED_IN)
        del db.room_rates["SINGLE"]

        with pytest.raises(RoomRateNotConfigured):
            CheckOutControl(uow).check_out(reservation_id)

        assert uow.db.charges == []
        assert uow.rollbacks == 1

    def test_raises_when_reservation_is_missing(self, uow: FakeUnitOfWork) -> None:
        with pytest.raises(ReservationNotFound):
            CheckOutControl(uow).check_out(uuid4())

    @pytest.mark.parametrize(
        "status",
        [
            ReservationStatus.RESERVED,
            ReservationStatus.CHECKED_OUT,
            ReservationStatus.CANCELLED,
        ],
    )
    def test_rejects_invalid_state_without_issuing_charge(
        self, uow: FakeUnitOfWork, db: FakeDatabase, status: ReservationStatus
    ) -> None:
        """チェックイン済み以外からはチェックアウトできず、請求も発行されない。"""
        reservation_id = add_reservation(db, status=status)

        with pytest.raises(InvalidReservationState):
            CheckOutControl(uow).check_out(reservation_id)

        assert uow.db.charges == []
        assert uow.db.reservations[reservation_id].status is status
        assert uow.commits == 0
