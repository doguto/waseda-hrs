"""料金・請求のDBアクセスadapter。sqlc生成コードをドメインモデルに変換する。"""

from datetime import date
from uuid import UUID

import sqlalchemy

from libs.domain.billing import RoomRate, ServiceUsage
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

    def create_paid_charge(
        self, *, reservation_id: UUID, amount: int, issued_date: date
    ) -> UUID:
        charge_id = self._charges.create_paid_charge(
            reservation_id=reservation_id, amount=amount, issued_date=issued_date
        )
        if charge_id is None:
            raise RuntimeError("CreatePaidCharge did not return an id")
        return charge_id
