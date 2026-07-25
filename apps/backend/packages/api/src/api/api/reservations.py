"""予約に関するroute(BCEのboundary)。
UC1 部屋の予約、UC4 予約内容の確認、UC2 チェックイン、UC3 チェックアウト、
UC5 予約のキャンセル。
ドメイン層が投げる例外をHTTPステータスへ変換するのがboundaryの責務。"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from libs.application.cancellation import CancellationControl
from libs.application.checkin import CheckInControl
from libs.application.checkout import CheckOutControl
from libs.application.inquiry import InquiryControl
from libs.application.reservation import ReservationControl
from libs.domain.billing import RoomRateNotConfigured
from libs.domain.reservation import (
    InvalidReservationPeriod,
    InvalidReservationState,
    NoAvailableRoom,
    ReservationNotFound,
)

from api.api.schemas.reservation import (
    ChargeResponse,
    CheckOutResponse,
    ReservationResponse,
    ReserveReservationRequest,
)
from api.services import (
    get_cancellation_control,
    get_check_in_control,
    get_check_out_control,
    get_inquiry_control,
    get_reservation_control,
)

router = APIRouter()


@router.post("/reservations", status_code=201)
def reserve_reservation(
    body: ReserveReservationRequest,
    control: ReservationControl = Depends(get_reservation_control),
) -> ReservationResponse:
    try:
        reservation = control.reserve(
            room_type=body.room_type,
            check_in_date=body.check_in_date,
            check_out_date=body.check_out_date,
            guest_name=body.guest_name,
            guest_contact=body.guest_contact,
        )
    except InvalidReservationPeriod as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from None
    except NoAvailableRoom as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None
    return ReservationResponse.from_domain(reservation)


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


@router.post("/reservations/{reservation_id}/check-out")
def check_out_reservation(
    reservation_id: UUID,
    control: CheckOutControl = Depends(get_check_out_control),
) -> CheckOutResponse:
    try:
        result = control.check_out(reservation_id)
    except ReservationNotFound:
        raise HTTPException(status_code=404, detail="reservation not found") from None
    except InvalidReservationState as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None
    except RoomRateNotConfigured as exc:
        raise HTTPException(
            status_code=409, detail=f"room rate not configured for room type {exc}"
        ) from None
    return CheckOutResponse(
        reservation=ReservationResponse.from_domain(result.reservation),
        charge=ChargeResponse(
            amount=result.charge.amount,
            issued_date=result.charge.issued_date,
            paid=result.charge.paid,
        ),
    )


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
