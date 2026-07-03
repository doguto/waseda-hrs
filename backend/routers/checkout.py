from fastapi import APIRouter, HTTPException, status

from schemas.response.checkout import ChargeResponse, CheckOutResponse
from schemas.response.error import ErrorResponse

router = APIRouter(prefix="/reservations", tags=["checkout"])


@router.get(
    "/{reservation_id}/charge",
    response_model=ChargeResponse,
    operation_id="calculate_charge",
    responses={404: {"model": ErrorResponse, "description": "該当する予約が存在しない"}},
)
def calculate_charge(reservation_id: str) -> ChargeResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.post(
    "/{reservation_id}/check-out",
    response_model=CheckOutResponse,
    operation_id="check_out_reservation",
    responses={404: {"model": ErrorResponse, "description": "該当する予約が存在しない"}},
)
def check_out_reservation(reservation_id: str) -> CheckOutResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
