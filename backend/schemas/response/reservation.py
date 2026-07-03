from datetime import date

from pydantic import BaseModel

from schemas.common import ReservationStatus


class ReservationCreateResponse(BaseModel):
    reservation_id: str


class ReservationDetailResponse(BaseModel):
    reservation_id: str
    room_type: str
    check_in_date: date
    check_out_date: date
    status: ReservationStatus
