"""UC3 チェックアウトする のコントロールに対するテスト。

UC3は「料金を計算して請求を発行する」「支払いを記録してチェックアウトを完了する」の
2段階に分かれる（08cの手順1と手順2）。支払いが行われなければ予約はCHECKED_INのまま
留まる必要があり、これが例外フロー5a（支払い拒否＝チェックアウト未完了）にあたる。
料金計算そのものはドメイン(billing)のテストで確認済みなので、ここでは段階の切り分けと
状態の遷移を確認する。
"""

from datetime import date
from uuid import uuid4

import pytest
from libs.application.checkout import CheckOutControl
from libs.domain.billing import ChargeNotFound, RoomRateNotConfigured, ServiceUsage
from libs.domain.reservation import (
    InvalidReservationState,
    ReservationNotFound,
    ReservationStatus,
    RoomStatus,
)

from tests.application.conftest import SINGLE_PRICE, add_charge, add_reservation
from tests.application.fakes import FakeDatabase, FakeUnitOfWork

THREE_NIGHTS = 3
ROOM_CHARGE = SINGLE_PRICE * THREE_NIGHTS


class TestIssueCharge:
    def test_charges_room_only_when_no_services(
        self, uow: FakeUnitOfWork, db: FakeDatabase
    ) -> None:
        """基本フロー手順2: 請求額 = 単価 × 泊数。"""
        reservation_id = add_reservation(db, status=ReservationStatus.CHECKED_IN)

        result = CheckOutControl(uow).issue_charge(reservation_id)

        assert result.charge.amount == ROOM_CHARGE
        assert result.charge.issued_date == date.today()
        assert uow.commits == 1

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

        result = CheckOutControl(uow).issue_charge(reservation_id)

        assert result.charge.amount == ROOM_CHARGE + 4200

    def test_issues_the_charge_unpaid_and_keeps_the_reservation_checked_in(
        self, uow: FakeUnitOfWork, db: FakeDatabase
    ) -> None:
        """請求の発行だけではチェックアウトは完了しない（支払いは別段階）。"""
        reservation_id = add_reservation(db, status=ReservationStatus.CHECKED_IN)

        result = CheckOutControl(uow).issue_charge(reservation_id)

        assert result.charge.paid is False
        assert result.reservation.status is ReservationStatus.CHECKED_IN
        assert (
            uow.db.reservations[reservation_id].status is ReservationStatus.CHECKED_IN
        )
        assert uow.db.rooms["101"].status is RoomStatus.OCCUPIED

    def test_does_not_reissue_an_existing_charge(
        self, uow: FakeUnitOfWork, db: FakeDatabase
    ) -> None:
        """発行済みなら再計算せず、同じ請求を返す（画面の再操作に耐える）。"""
        reservation_id = add_reservation(db, status=ReservationStatus.CHECKED_IN)
        add_charge(db, reservation_id, amount=99999, paid=False)

        result = CheckOutControl(uow).issue_charge(reservation_id)

        assert result.charge.amount == 99999
        assert len(uow.db.charges) == 1

    def test_raises_when_room_rate_is_not_configured(
        self, uow: FakeUnitOfWork, db: FakeDatabase
    ) -> None:
        """料金表が無い客室タイプは請求を作らずに失敗する。"""
        reservation_id = add_reservation(db, status=ReservationStatus.CHECKED_IN)
        del db.room_rates["SINGLE"]

        with pytest.raises(RoomRateNotConfigured):
            CheckOutControl(uow).issue_charge(reservation_id)

        assert uow.db.charges == {}
        assert uow.rollbacks == 1

    def test_raises_when_reservation_is_missing(self, uow: FakeUnitOfWork) -> None:
        with pytest.raises(ReservationNotFound):
            CheckOutControl(uow).issue_charge(uuid4())

    @pytest.mark.parametrize(
        "status", [ReservationStatus.RESERVED, ReservationStatus.CANCELLED]
    )
    def test_rejects_invalid_state_without_issuing_charge(
        self, uow: FakeUnitOfWork, db: FakeDatabase, status: ReservationStatus
    ) -> None:
        """チェックイン済み以外の予約には請求を発行しない。"""
        reservation_id = add_reservation(db, status=status)

        with pytest.raises(InvalidReservationState):
            CheckOutControl(uow).issue_charge(reservation_id)

        assert uow.db.charges == {}
        assert uow.commits == 0


class TestFindCharge:
    def test_returns_the_issued_charge(
        self, uow: FakeUnitOfWork, db: FakeDatabase
    ) -> None:
        """画面を開き直したときに発行済みの請求を読み直せる。"""
        reservation_id = add_reservation(db, status=ReservationStatus.CHECKED_IN)
        add_charge(db, reservation_id, amount=ROOM_CHARGE, paid=False)

        charge = CheckOutControl(uow).find_charge(reservation_id)

        assert charge is not None
        assert charge.amount == ROOM_CHARGE
        assert charge.paid is False

    def test_returns_none_before_the_charge_is_issued(
        self, uow: FakeUnitOfWork, db: FakeDatabase
    ) -> None:
        reservation_id = add_reservation(db, status=ReservationStatus.CHECKED_IN)

        assert CheckOutControl(uow).find_charge(reservation_id) is None

    def test_uses_read_only_transaction(
        self, uow: FakeUnitOfWork, db: FakeDatabase
    ) -> None:
        """参照だけなので書き込み用トランザクションを開かない。"""
        reservation_id = add_reservation(db, status=ReservationStatus.CHECKED_IN)

        CheckOutControl(uow).find_charge(reservation_id)

        assert uow.reads == 1
        assert uow.commits == 0


class TestPay:
    def test_records_payment_and_completes_check_out(
        self, uow: FakeUnitOfWork, db: FakeDatabase
    ) -> None:
        """基本フロー手順6・7: 支払いを記録し、予約と客室の状態を進める。"""
        reservation_id = add_reservation(db, status=ReservationStatus.CHECKED_IN)
        add_charge(db, reservation_id, amount=ROOM_CHARGE, paid=False)

        result = CheckOutControl(uow).pay(reservation_id)

        assert result.charge.paid is True
        assert result.reservation.status is ReservationStatus.CHECKED_OUT
        assert (
            uow.db.reservations[reservation_id].status is ReservationStatus.CHECKED_OUT
        )
        assert uow.db.rooms["101"].status is RoomStatus.VACANT
        assert uow.commits == 1

    def test_locks_reservation_and_charge_before_updating(
        self, uow: FakeUnitOfWork, db: FakeDatabase
    ) -> None:
        reservation_id = add_reservation(db, status=ReservationStatus.CHECKED_IN)
        add_charge(db, reservation_id, amount=ROOM_CHARGE, paid=False)

        CheckOutControl(uow).pay(reservation_id)

        assert uow.db.locked_reservation_ids == [reservation_id]
        assert uow.db.locked_charge_ids == [reservation_id]

    def test_is_idempotent_once_paid(
        self, uow: FakeUnitOfWork, db: FakeDatabase
    ) -> None:
        """支払い済みの予約に再度払っても状態は変わらない（二重送信に耐える）。"""
        reservation_id = add_reservation(db, status=ReservationStatus.CHECKED_OUT)
        add_charge(db, reservation_id, amount=ROOM_CHARGE, paid=True)

        result = CheckOutControl(uow).pay(reservation_id)

        assert result.charge.paid is True
        assert result.reservation.status is ReservationStatus.CHECKED_OUT

    def test_raises_when_the_charge_is_not_issued_yet(
        self, uow: FakeUnitOfWork, db: FakeDatabase
    ) -> None:
        """請求の発行前に支払いは記録できない。"""
        reservation_id = add_reservation(db, status=ReservationStatus.CHECKED_IN)

        with pytest.raises(ChargeNotFound):
            CheckOutControl(uow).pay(reservation_id)

        assert (
            uow.db.reservations[reservation_id].status is ReservationStatus.CHECKED_IN
        )
        assert uow.rollbacks == 1

    def test_raises_when_reservation_is_missing(self, uow: FakeUnitOfWork) -> None:
        with pytest.raises(ReservationNotFound):
            CheckOutControl(uow).pay(uuid4())
