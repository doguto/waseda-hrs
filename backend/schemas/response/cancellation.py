from pydantic import BaseModel

from schemas.common import ReservationStatus


class CancellationResponse(BaseModel):
    reservation_id: str
    status: ReservationStatus
