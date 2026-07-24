"""予約のDBアクセスadapter。sqlc生成コードをドメインモデルに変換し、
Application層がsqlcへ直接依存しないようにする。"""

from datetime import date
from typing import Protocol
from uuid import UUID

import sqlalchemy

from libs.domain.reservation import (
    Guest,
    Reservation,
    ReservationStatus,
    Room,
    RoomStatus,
)
from libs.infrastructure.db.gen import models
from libs.infrastructure.db.gen.guest import Querier as GuestQuerier
from libs.infrastructure.db.gen.reservation import Querier as ReservationQuerier
from libs.infrastructure.db.gen.room import Querier as RoomQuerier


class _ReservationDetailRow(Protocol):
    """GetReservationById / LockReservationDetailById が返す行の共通形。"""

    id: UUID
    check_in_date: date
    check_out_date: date
    status: models.ReservationStatus
    guest_name: str
    guest_contact: str
    room_number: str
    room_type: str


def _to_reservation(row: _ReservationDetailRow) -> Reservation:
    return Reservation(
        id=row.id,
        check_in_date=row.check_in_date,
        check_out_date=row.check_out_date,
        status=ReservationStatus(row.status.value),
        guest=Guest(name=row.guest_name, contact=row.guest_contact),
        room=Room(room_number=row.room_number, room_type=row.room_type),
    )


class ReservationRepository:
    def __init__(self, conn: sqlalchemy.engine.Connection) -> None:
        self._reservations = ReservationQuerier(conn)
        self._rooms = RoomQuerier(conn)
        self._guests = GuestQuerier(conn)

    def find_by_id(self, reservation_id: UUID) -> Reservation | None:
        row = self._reservations.get_reservation_by_id(id=reservation_id)
        return _to_reservation(row) if row is not None else None

    def lock_by_id(self, reservation_id: UUID) -> Reservation | None:
        """予約と客室の行をロックしたうえで取得する(状態を書き換える前提の読み取り)。"""
        row = self._reservations.lock_reservation_detail_by_id(id=reservation_id)
        return _to_reservation(row) if row is not None else None

    def set_status(self, reservation_id: UUID, status: ReservationStatus) -> None:
        self._reservations.set_reservation_status(
            id=reservation_id, status=models.ReservationStatus(status.value)
        )

    def set_room_status(self, room_number: str, status: RoomStatus) -> None:
        self._rooms.set_room_status(
            room_number=room_number, status=models.RoomStatus(status.value)
        )

    def find_and_lock_vacant_room(self, room_type: str) -> Room | None:
        """指定タイプの空室を1つロックして返す。空室が無ければ None。"""
        row = self._rooms.find_and_lock_vacant_room(room_type=room_type)
        if row is None:
            return None
        return Room(room_number=row.room_number, room_type=row.room_type)

    def create_guest(self, guest: Guest) -> UUID:
        guest_id = self._guests.create_guest(name=guest.name, contact=guest.contact)
        if guest_id is None:
            raise RuntimeError("CreateGuest did not return an id")
        return guest_id

    def create_reservation(
        self,
        *,
        guest_id: UUID,
        room_number: str,
        check_in_date: date,
        check_out_date: date,
    ) -> UUID:
        reservation_id = self._reservations.create_reservation(
            guest_id=guest_id,
            room_number=room_number,
            check_in_date=check_in_date,
            check_out_date=check_out_date,
        )
        if reservation_id is None:
            raise RuntimeError("CreateReservation did not return an id")
        return reservation_id
