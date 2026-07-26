"""アプリケーション層テストの共通フィクスチャ。

`libs.domain.repositories.UnitOfWork`(ポート)を満たすフェイクを注入するだけで
各Controlが動くことを、型注釈の上でも確認する
（`UnitOfWork` として宣言した変数に `FakeUnitOfWork` を代入し、mypy strict に通す）。
"""

from datetime import date
from uuid import UUID, uuid4

import pytest
from libs.domain.billing import ServiceUsage
from libs.domain.repositories import UnitOfWork
from libs.domain.reservation import Guest, ReservationStatus, RoomStatus

from tests.application.fakes import (
    FakeDatabase,
    FakeUnitOfWork,
    ReservationRow,
    RoomRow,
)

CHECK_IN_DATE = date(2026, 8, 1)
CHECK_OUT_DATE = date(2026, 8, 4)  # 3泊
SINGLE_PRICE = 12000


@pytest.fixture
def db() -> FakeDatabase:
    """シングル2室・ツイン1室、単価設定済みのホテル。予約はまだ無い。"""
    return FakeDatabase(
        rooms={
            "101": RoomRow("101", "SINGLE", RoomStatus.VACANT),
            "102": RoomRow("102", "SINGLE", RoomStatus.VACANT),
            "201": RoomRow("201", "TWIN", RoomStatus.VACANT),
        },
        room_rates={"SINGLE": SINGLE_PRICE, "TWIN": 20000},
    )


@pytest.fixture
def uow(db: FakeDatabase) -> FakeUnitOfWork:
    return FakeUnitOfWork(db)


@pytest.fixture
def port(uow: FakeUnitOfWork) -> UnitOfWork:
    """フェイクがポートの型として通ることの確認を兼ねたフィクスチャ。"""
    return uow


def add_reservation(
    db: FakeDatabase,
    *,
    status: ReservationStatus,
    room_number: str = "101",
    services: list[ServiceUsage] | None = None,
) -> UUID:
    """指定状態の予約を1件仕込む。客室の状態は予約の状態に合わせる。"""
    guest_id = uuid4()
    db.guests[guest_id] = Guest(name="山田太郎", contact="yamada@example.com")
    reservation_id = uuid4()
    db.reservations[reservation_id] = ReservationRow(
        id=reservation_id,
        guest_id=guest_id,
        room_number=room_number,
        check_in_date=CHECK_IN_DATE,
        check_out_date=CHECK_OUT_DATE,
        status=status,
    )
    db.rooms[room_number].status = {
        ReservationStatus.RESERVED: RoomStatus.RESERVED,
        ReservationStatus.CHECKED_IN: RoomStatus.OCCUPIED,
        ReservationStatus.CHECKED_OUT: RoomStatus.VACANT,
        ReservationStatus.CANCELLED: RoomStatus.VACANT,
    }[status]
    if services:
        db.service_usages[reservation_id] = services
    return reservation_id
