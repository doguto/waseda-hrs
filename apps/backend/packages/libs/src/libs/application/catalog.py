"""部屋タイプ閲覧のコントロール(読み取り)。"""

from libs.domain.catalog import RoomTypeSummary
from libs.domain.repositories import UnitOfWork


class CatalogControl:
    def __init__(self, uow: UnitOfWork) -> None:
        self._uow = uow

    def list_room_types(self) -> list[RoomTypeSummary]:
        with self._uow.read() as repositories:
            return repositories.catalog.list_room_types()

    def find_room_type(self, room_type: str) -> RoomTypeSummary | None:
        with self._uow.read() as repositories:
            return repositories.catalog.find_room_type(room_type)
