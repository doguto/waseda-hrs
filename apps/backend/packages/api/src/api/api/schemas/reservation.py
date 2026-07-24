"""予約APIのrequest/response schema(BCEのboundary)。
ドメインモデルとHTTP表現を相互に変換する。"""

from datetime import date
from uuid import UUID

import pydantic
from libs.domain.reservation import Reservation, ReservationStatus


class ReserveReservationRequest(pydantic.BaseModel):
    room_type: str
    check_in_date: date
    check_out_date: date
    guest_name: str
    guest_contact: str


class ReservationResponse(pydantic.BaseModel):
    reservation_id: UUID
    check_in_date: date
    check_out_date: date
    status: ReservationStatus
    guest_name: str
    guest_contact: str
    room_number: str
    room_type: str

    @classmethod
    def from_domain(cls, reservation: Reservation) -> "ReservationResponse":
        return cls(
            reservation_id=reservation.id,
            check_in_date=reservation.check_in_date,
            check_out_date=reservation.check_out_date,
            status=reservation.status,
            guest_name=reservation.guest.name,
            guest_contact=reservation.guest.contact,
            room_number=reservation.room.room_number,
            room_type=reservation.room.room_type,
        )
