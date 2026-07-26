"""部屋タイプ閲覧のコントロールに対するテスト（予約前のブラウズ）。"""

from libs.application.catalog import CatalogControl
from libs.domain.reservation import ReservationStatus, RoomStatus

from tests.application.conftest import SINGLE_PRICE, add_reservation
from tests.application.fakes import FakeDatabase, FakeUnitOfWork


class TestListRoomTypes:
    def test_lists_each_room_type_with_price_and_vacancy(
        self, uow: FakeUnitOfWork
    ) -> None:
        summaries = {s.room_type: s for s in CatalogControl(uow).list_room_types()}

        assert set(summaries) == {"SINGLE", "TWIN"}
        assert summaries["SINGLE"].price_per_night == SINGLE_PRICE
        assert summaries["SINGLE"].vacant_count == 2
        assert summaries["TWIN"].vacant_count == 1

    def test_vacant_count_excludes_reserved_rooms(
        self, uow: FakeUnitOfWork, db: FakeDatabase
    ) -> None:
        add_reservation(db, status=ReservationStatus.RESERVED, room_number="101")

        summaries = {s.room_type: s for s in CatalogControl(uow).list_room_types()}

        assert db.rooms["101"].status is RoomStatus.RESERVED
        assert summaries["SINGLE"].vacant_count == 1

    def test_uses_read_only_transaction(self, uow: FakeUnitOfWork) -> None:
        CatalogControl(uow).list_room_types()

        assert uow.reads == 1
        assert uow.commits == 0


class TestFindRoomType:
    def test_returns_summary_for_known_type(self, uow: FakeUnitOfWork) -> None:
        summary = CatalogControl(uow).find_room_type("TWIN")

        assert summary is not None
        assert summary.price_per_night == 20000

    def test_returns_none_for_unknown_type(self, uow: FakeUnitOfWork) -> None:
        assert CatalogControl(uow).find_room_type("SUITE") is None
