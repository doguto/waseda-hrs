"""部屋タイプ閲覧のDBアクセスadapter。"""

import sqlalchemy

from libs.domain.catalog import RoomTypeSummary
from libs.infrastructure.db.gen.room_type import Querier as RoomTypeQuerier


class CatalogRepository:
    def __init__(self, conn: sqlalchemy.engine.Connection) -> None:
        self._room_types = RoomTypeQuerier(conn)

    def list_room_types(self) -> list[RoomTypeSummary]:
        return [
            RoomTypeSummary(
                room_type=row.room_type,
                price_per_night=row.price_per_night,
                vacant_count=row.vacant_count,
            )
            for row in self._room_types.list_room_types()
        ]

    def find_room_type(self, room_type: str) -> RoomTypeSummary | None:
        row = self._room_types.get_room_type(room_type=room_type)
        if row is None:
            return None
        return RoomTypeSummary(
            room_type=row.room_type,
            price_per_night=row.price_per_night,
            vacant_count=row.vacant_count,
        )
