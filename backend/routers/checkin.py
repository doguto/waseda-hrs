from fastapi import APIRouter, HTTPException, status

from schemas.response.checkin import CheckInResponse
from schemas.response.error import ErrorResponse

router = APIRouter(prefix="/reservations", tags=["checkin"])


@router.post(
    "/{reservation_id}/check-in",
    response_model=CheckInResponse,
    operation_id="check_in_reservation",
    responses={404: {"model": ErrorResponse, "description": "該当する予約が存在しない"}},
)
def check_in_reservation(reservation_id: str) -> CheckInResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
