"""料金・請求のDBアクセスadapter。sqlc生成コードをドメインモデルに変換する。"""

from datetime import date
from uuid import UUID

import sqlalchemy

from libs.domain.billing import Charge, RoomRate, ServiceUsage
from libs.infrastructure.db.gen.charge import Querier as ChargeQuerier
from libs.infrastructure.db.gen.room_rate import Querier as RoomRateQuerier
from libs.infrastructure.db.gen.service_usage import Querier as ServiceUsageQuerier


class DbBillingRepository:
    def __init__(self, conn: sqlalchemy.engine.Connection) -> None:
        self._room_rates = RoomRateQuerier(conn)
        self._service_usages = ServiceUsageQuerier(conn)
        self._charges = ChargeQuerier(conn)

    def find_room_rate(self, room_type: str) -> RoomRate | None:
        row = self._room_rates.get_room_rate(room_type=room_type)
        if row is None:
            return None
        return RoomRate(room_type=row.room_type, price_per_night=row.price_per_night)

    def list_service_usages(self, reservation_id: UUID) -> list[ServiceUsage]:
        return [
            ServiceUsage(service_name=row.service_name, fee=row.fee)
            for row in self._service_usages.list_service_usages(
                reservation_id=reservation_id
            )
        ]

    def create_charge(
        self, *, reservation_id: UUID, amount: int, issued_date: date
    ) -> Charge:
        row = self._charges.create_charge(
            reservation_id=reservation_id, amount=amount, issued_date=issued_date
        )
        if row is None:
            raise RuntimeError("CreateCharge did not return a charge")
        return Charge(amount=row.amount, issued_date=row.issued_date, paid=row.paid)

    def find_charge(self, reservation_id: UUID) -> Charge | None:
        row = self._charges.get_charge_by_reservation_id(reservation_id=reservation_id)
        if row is None:
            return None
        return Charge(amount=row.amount, issued_date=row.issued_date, paid=row.paid)

    def lock_charge(self, reservation_id: UUID) -> Charge | None:
        row = self._charges.lock_charge_by_reservation_id(reservation_id=reservation_id)
        if row is None:
            return None
        return Charge(amount=row.amount, issued_date=row.issued_date, paid=row.paid)

    def mark_charge_paid(self, reservation_id: UUID) -> Charge:
        row = self._charges.mark_charge_paid(reservation_id=reservation_id)
        if row is None:
            raise RuntimeError("MarkChargePaid did not return a charge")
        return Charge(amount=row.amount, issued_date=row.issued_date, paid=row.paid)
