"""予約に関するroute(BCEのboundary)。
UC4 予約内容の確認、UC2 チェックイン、UC5 予約のキャンセル。
ドメイン層が投げる例外をHTTPステータスへ変換するのがboundaryの責務。"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from libs.application.cancellation import CancellationControl
from libs.application.checkin import CheckInControl
from libs.application.inquiry import InquiryControl
from libs.domain.reservation import InvalidReservationState, ReservationNotFound

from api.api.schemas.reservation import ReservationResponse
from api.services import (
    get_cancellation_control,
    get_check_in_control,
    get_inquiry_control,
)

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


@router.post("/reservations/{reservation_id}/check-in")
def check_in_reservation(
    reservation_id: UUID,
    control: CheckInControl = Depends(get_check_in_control),
) -> ReservationResponse:
    try:
        reservation = control.check_in(reservation_id)
    except ReservationNotFound:
        raise HTTPException(status_code=404, detail="reservation not found") from None
    except InvalidReservationState as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None
    return ReservationResponse.from_domain(reservation)


@router.post("/reservations/{reservation_id}/cancellation")
def cancel_reservation(
    reservation_id: UUID,
    control: CancellationControl = Depends(get_cancellation_control),
) -> ReservationResponse:
    try:
        reservation = control.cancel_reservation(reservation_id)
    except ReservationNotFound:
        raise HTTPException(status_code=404, detail="reservation not found") from None
    except InvalidReservationState as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None
    return ReservationResponse.from_domain(reservation)
