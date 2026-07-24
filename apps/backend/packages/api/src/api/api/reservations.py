"""UC4 予約内容を確認する のroute(BCEのboundary)。"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from libs.application.inquiry import InquiryControl

from api.api.schemas.reservation import ReservationResponse
from api.services import get_inquiry_control

router = APIRouter()


@router.get("/reservations/{reservation_id}")
def get_reservation(
    reservation_id: UUID,
    control: InquiryControl = Depends(get_inquiry_control),
) -> ReservationResponse:
    reservation = control.find_reservation(reservation_id)
    if reservation is None:
        raise HTTPException(status_code=404, detail="reservation not found")
    return ReservationResponse.from_domain(reservation)
