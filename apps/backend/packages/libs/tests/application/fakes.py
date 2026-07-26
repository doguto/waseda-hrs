"""アプリケーション層のテスト用インメモリ実装。

`libs.domain.repositories` のポート(Protocol)を満たすフェイクを用意し、
Control をDBなしで動かす。Control が具象のDBアクセスに依存していないことは、
このフェイクを渡してテストが通ること自体が示している。

トランザクションの振る舞い(例外時のロールバック)も再現するため、
`begin()` は開始時のスナップショットを取り、例外なら状態を巻き戻す。
"""

from collections.abc import Iterator
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import date
from uuid import UUID, uuid4

from libs.domain.billing import RoomRate, ServiceUsage
from libs.domain.catalog import RoomTypeSummary
from libs.domain.reservation import (
    Guest,
    Reservation,
    ReservationStatus,
    Room,
    RoomStatus,
)


@dataclass
class RoomRow:
    room_number: str
    room_type: str
    status: RoomStatus


@dataclass
class ReservationRow:
    id: UUID
    guest_id: UUID
    room_number: str
    check_in_date: date
    check_out_date: date
    status: ReservationStatus


@dataclass
class ChargeRow:
    reservation_id: UUID
    amount: int
    issued_date: date
    paid: bool


@dataclass
class FakeDatabase:
    guests: dict[UUID, Guest] = field(default_factory=dict)
    rooms: dict[str, RoomRow] = field(default_factory=dict)
    reservations: dict[UUID, ReservationRow] = field(default_factory=dict)
    room_rates: dict[str, int] = field(default_factory=dict)
    service_usages: dict[UUID, list[ServiceUsage]] = field(default_factory=dict)
    charges: list[ChargeRow] = field(default_factory=list)

    # 「書き換える前に行をロックしたか」を検証するための記録。
    locked_reservation_ids: list[UUID] = field(default_factory=list)
    locked_room_types: list[str] = field(default_factory=list)


class FakeReservationRepository:
    def __init__(self, db: FakeDatabase) -> None:
        self._db = db

    def _build(self, row: ReservationRow) -> Reservation:
        room = self._db.rooms[row.room_number]
        return Reservation(
            id=row.id,
            check_in_date=row.check_in_date,
            check_out_date=row.check_out_date,
            status=row.status,
            guest=self._db.guests[row.guest_id],
            room=Room(room_number=room.room_number, room_type=room.room_type),
        )

    def find_by_id(self, reservation_id: UUID) -> Reservation | None:
        row = self._db.reservations.get(reservation_id)
        return self._build(row) if row is not None else None

    def lock_by_id(self, reservation_id: UUID) -> Reservation | None:
        self._db.locked_reservation_ids.append(reservation_id)
        return self.find_by_id(reservation_id)

    def set_status(self, reservation_id: UUID, status: ReservationStatus) -> None:
        self._db.reservations[reservation_id].status = status

    def set_room_status(self, room_number: str, status: RoomStatus) -> None:
        self._db.rooms[room_number].status = status

    def find_and_lock_vacant_room(self, room_type: str) -> Room | None:
        self._db.locked_room_types.append(room_type)
        for row in self._db.rooms.values():
            if row.room_type == room_type and row.status is RoomStatus.VACANT:
                return Room(room_number=row.room_number, room_type=row.room_type)
        return None

    def create_guest(self, guest: Guest) -> UUID:
        guest_id = uuid4()
        self._db.guests[guest_id] = guest
        return guest_id

    def create_reservation(
        self,
        *,
        guest_id: UUID,
        room_number: str,
        check_in_date: date,
        check_out_date: date,
    ) -> UUID:
        reservation_id = uuid4()
        self._db.reservations[reservation_id] = ReservationRow(
            id=reservation_id,
            guest_id=guest_id,
            room_number=room_number,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
            status=ReservationStatus.RESERVED,
        )
        return reservation_id


class FakeBillingRepository:
    def __init__(self, db: FakeDatabase) -> None:
        self._db = db

    def find_room_rate(self, room_type: str) -> RoomRate | None:
        price = self._db.room_rates.get(room_type)
        if price is None:
            return None
        return RoomRate(room_type=room_type, price_per_night=price)

    def list_service_usages(self, reservation_id: UUID) -> list[ServiceUsage]:
        return list(self._db.service_usages.get(reservation_id, []))

    def create_paid_charge(
        self, *, reservation_id: UUID, amount: int, issued_date: date
    ) -> UUID:
        self._db.charges.append(
            ChargeRow(
                reservation_id=reservation_id,
                amount=amount,
                issued_date=issued_date,
                paid=True,
            )
        )
        return uuid4()


class FakeCatalogRepository:
    def __init__(self, db: FakeDatabase) -> None:
        self._db = db

    def _summarize(self, room_type: str) -> RoomTypeSummary:
        return RoomTypeSummary(
            room_type=room_type,
            price_per_night=self._db.room_rates[room_type],
            vacant_count=sum(
                1
                for row in self._db.rooms.values()
                if row.room_type == room_type and row.status is RoomStatus.VACANT
            ),
        )

    def list_room_types(self) -> list[RoomTypeSummary]:
        return [self._summarize(room_type) for room_type in self._db.room_rates]

    def find_room_type(self, room_type: str) -> RoomTypeSummary | None:
        if room_type not in self._db.room_rates:
            return None
        return self._summarize(room_type)


@dataclass(frozen=True)
class FakeRepositories:
    reservations: FakeReservationRepository
    billing: FakeBillingRepository
    catalog: FakeCatalogRepository

    @classmethod
    def bind(cls, db: FakeDatabase) -> "FakeRepositories":
        return cls(
            reservations=FakeReservationRepository(db),
            billing=FakeBillingRepository(db),
            catalog=FakeCatalogRepository(db),
        )


class FakeUnitOfWork:
    """例外でロールバック、正常終了でコミットする振る舞いを再現する。"""

    def __init__(self, db: FakeDatabase | None = None) -> None:
        self.db = db if db is not None else FakeDatabase()
        self.commits = 0
        self.rollbacks = 0
        self.reads = 0

    @contextmanager
    def begin(self) -> Iterator[FakeRepositories]:
        snapshot = deepcopy(self.db)
        try:
            yield FakeRepositories.bind(self.db)
        except BaseException:
            self.db = snapshot
            self.rollbacks += 1
            raise
        self.commits += 1

    @contextmanager
    def read(self) -> Iterator[FakeRepositories]:
        self.reads += 1
        yield FakeRepositories.bind(self.db)
