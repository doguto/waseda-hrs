"""予約エンティティの不変条件(状態遷移の可否)と宿泊期間の検査に対するテスト。
09のクラス図で Reservation に持たせた操作が、分析で決めた状態遷移だけを
許すことを確認する。DBやHTTPには依存しない純粋なドメインのテスト。"""

from datetime import date
from uuid import uuid4

import pytest
from libs.domain.reservation import (
    Guest,
    InvalidReservationPeriod,
    InvalidReservationState,
    Reservation,
    ReservationStatus,
    Room,
    ensure_reservable_period,
)


def make_reservation(status: ReservationStatus) -> Reservation:
    """指定した状態の予約を1件つくる(3泊: 8/1 -> 8/4)。"""
    return Reservation(
        id=uuid4(),
        check_in_date=date(2026, 8, 1),
        check_out_date=date(2026, 8, 4),
        status=status,
        guest=Guest(name="山田太郎", contact="yamada@example.com"),
        room=Room(room_number="101", room_type="SINGLE"),
    )


class TestEnsureReservablePeriod:
    def test_accepts_check_out_after_check_in(self) -> None:
        """チェックアウトがチェックインより後なら通る。"""
        ensure_reservable_period(date(2026, 8, 1), date(2026, 8, 2))

    def test_rejects_same_day(self) -> None:
        """同日のチェックイン・チェックアウト(0泊)は認めない。"""
        with pytest.raises(InvalidReservationPeriod):
            ensure_reservable_period(date(2026, 8, 1), date(2026, 8, 1))

    def test_rejects_reversed_period(self) -> None:
        """チェックアウトがチェックインより前は認めない。"""
        with pytest.raises(InvalidReservationPeriod):
            ensure_reservable_period(date(2026, 8, 4), date(2026, 8, 1))


class TestCheckIn:
    def test_reserved_becomes_checked_in(self) -> None:
        """UC2 基本系列: RESERVED の予約はチェックインできる。"""
        reservation = make_reservation(ReservationStatus.RESERVED)

        checked_in = reservation.check_in()

        assert checked_in.status is ReservationStatus.CHECKED_IN
        assert checked_in.id == reservation.id
        # frozen dataclass なので元のインスタンスは書き換わらない。
        assert reservation.status is ReservationStatus.RESERVED

    @pytest.mark.parametrize(
        "status",
        [
            ReservationStatus.CHECKED_IN,
            ReservationStatus.CHECKED_OUT,
            ReservationStatus.CANCELLED,
        ],
    )
    def test_rejects_other_statuses(self, status: ReservationStatus) -> None:
        """UC2 例外系列: RESERVED 以外はチェックインできない(二重チェックイン等)。"""
        with pytest.raises(InvalidReservationState):
            make_reservation(status).check_in()


class TestCheckOut:
    def test_checked_in_becomes_checked_out(self) -> None:
        """UC3 基本系列: CHECKED_IN の予約はチェックアウトできる。"""
        reservation = make_reservation(ReservationStatus.CHECKED_IN)

        checked_out = reservation.check_out()

        assert checked_out.status is ReservationStatus.CHECKED_OUT
        assert reservation.status is ReservationStatus.CHECKED_IN

    @pytest.mark.parametrize(
        "status",
        [
            ReservationStatus.RESERVED,
            ReservationStatus.CHECKED_OUT,
            ReservationStatus.CANCELLED,
        ],
    )
    def test_rejects_other_statuses(self, status: ReservationStatus) -> None:
        """UC3 例外系列: 未チェックイン・既チェックアウトはチェックアウトできない。"""
        with pytest.raises(InvalidReservationState):
            make_reservation(status).check_out()


class TestCancel:
    def test_reserved_becomes_cancelled(self) -> None:
        """UC5 基本系列: RESERVED の予約はキャンセルできる。"""
        reservation = make_reservation(ReservationStatus.RESERVED)

        cancelled = reservation.cancel()

        assert cancelled.status is ReservationStatus.CANCELLED
        assert reservation.status is ReservationStatus.RESERVED

    @pytest.mark.parametrize(
        "status",
        [
            ReservationStatus.CHECKED_IN,
            ReservationStatus.CHECKED_OUT,
            ReservationStatus.CANCELLED,
        ],
    )
    def test_rejects_other_statuses(self, status: ReservationStatus) -> None:
        """UC5 例外系列: 滞在中・滞在後・既キャンセルの予約はキャンセルできない。"""
        with pytest.raises(InvalidReservationState):
            make_reservation(status).cancel()


class TestNights:
    def test_counts_days_between_dates(self) -> None:
        """泊数はチェックアウト日とチェックイン日の差。"""
        assert make_reservation(ReservationStatus.RESERVED).nights() == 3

    def test_counts_one_night(self) -> None:
        """連泊しない場合は1泊。"""
        reservation = Reservation(
            id=uuid4(),
            check_in_date=date(2026, 8, 1),
            check_out_date=date(2026, 8, 2),
            status=ReservationStatus.RESERVED,
            guest=Guest(name="山田太郎", contact="yamada@example.com"),
            room=Room(room_number="101", room_type="SINGLE"),
        )

        assert reservation.nights() == 1


class TestStateTransitionSequence:
    def test_reserve_to_check_out(self) -> None:
        """予約 -> チェックイン -> チェックアウト と連続して遷移できる。"""
        reservation = make_reservation(ReservationStatus.RESERVED)

        result = reservation.check_in().check_out()

        assert result.status is ReservationStatus.CHECKED_OUT

    def test_cannot_check_in_after_cancel(self) -> None:
        """キャンセル後にチェックインへ戻ることはできない。"""
        cancelled = make_reservation(ReservationStatus.RESERVED).cancel()

        with pytest.raises(InvalidReservationState):
            cancelled.check_in()
