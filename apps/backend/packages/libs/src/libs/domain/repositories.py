"""永続化のポート(抽象インタフェース)。

アプリケーション層(Control)はここで宣言した Protocol にのみ依存し、
データソース層の具象クラス(libs.infrastructure.db)を知らない。依存の向きは
「データソース層 → ドメイン層」となり、依存性の逆転が成立する。
Protocol による構造的部分型なので、実装側はこのモジュールを import しない。

トランザクション境界はアプリケーション層に置くという設計を保つため、
接続の開閉は UnitOfWork が受け持ち、Control は begin() / read() を呼ぶだけにする。
"""

from contextlib import AbstractContextManager
from datetime import date
from typing import Protocol
from uuid import UUID

from libs.domain.billing import Charge, RoomRate, ServiceUsage
from libs.domain.catalog import RoomTypeSummary
from libs.domain.reservation import (
    Guest,
    Reservation,
    ReservationStatus,
    Room,
    RoomStatus,
)


class ReservationRepository(Protocol):
    """予約・客室・利用者の永続化。"""

    def find_by_id(self, reservation_id: UUID) -> Reservation | None: ...

    def lock_by_id(self, reservation_id: UUID) -> Reservation | None:
        """状態を書き換える前提で、予約と客室の行をロックして取得する。"""
        ...

    def set_status(self, reservation_id: UUID, status: ReservationStatus) -> None: ...

    def set_room_status(self, room_number: str, status: RoomStatus) -> None: ...

    def find_and_lock_vacant_room(self, room_type: str) -> Room | None:
        """指定タイプの空室を1つロックして返す。空室が無ければ None。"""
        ...

    def create_guest(self, guest: Guest) -> UUID: ...

    def create_reservation(
        self,
        *,
        guest_id: UUID,
        room_number: str,
        check_in_date: date,
        check_out_date: date,
    ) -> UUID: ...


class BillingRepository(Protocol):
    """料金表・追加サービス・請求の永続化。"""

    def find_room_rate(self, room_type: str) -> RoomRate | None: ...

    def list_service_usages(self, reservation_id: UUID) -> list[ServiceUsage]: ...

    def create_charge(
        self, *, reservation_id: UUID, amount: int, issued_date: date
    ) -> Charge: ...

    def find_charge(self, reservation_id: UUID) -> Charge | None: ...

    def lock_charge(self, reservation_id: UUID) -> Charge | None:
        """支払いを記録する前提で、請求の行をロックして取得する。"""
        ...

    def mark_charge_paid(self, reservation_id: UUID) -> Charge: ...


class CatalogRepository(Protocol):
    """部屋タイプ閲覧(読み取り専用)。"""

    def list_room_types(self) -> list[RoomTypeSummary]: ...

    def find_room_type(self, room_type: str) -> RoomTypeSummary | None: ...


class Repositories(Protocol):
    """1つのトランザクションに属するリポジトリの組。"""

    @property
    def reservations(self) -> ReservationRepository: ...

    @property
    def billing(self) -> BillingRepository: ...

    @property
    def catalog(self) -> CatalogRepository: ...


class UnitOfWork(Protocol):
    """トランザクション境界。Control はこの2つの入口だけを使う。"""

    def begin(self) -> AbstractContextManager[Repositories]:
        """書き込みを含む処理。正常終了でコミット、例外でロールバックする。"""
        ...

    def read(self) -> AbstractContextManager[Repositories]:
        """読み取りのみの処理。"""
        ...
