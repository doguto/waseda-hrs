"""部屋タイプ閲覧のコントロール(読み取り)。"""

import sqlalchemy

from libs.domain.catalog import RoomTypeSummary
from libs.infrastructure.db.repositories.catalog import CatalogRepository


class CatalogControl:
    def __init__(self, engine: sqlalchemy.Engine) -> None:
        self._engine = engine

    def list_room_types(self) -> list[RoomTypeSummary]:
        with self._engine.connect() as conn:
            return CatalogRepository(conn).list_room_types()

    def find_room_type(self, room_type: str) -> RoomTypeSummary | None:
        with self._engine.connect() as conn:
            return CatalogRepository(conn).find_room_type(room_type)
