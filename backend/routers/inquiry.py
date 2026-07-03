from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from schemas.request.reservation import ReservationInquiryQuery
from schemas.response.error import ErrorResponse
from schemas.response.reservation import ReservationDetailResponse

router = APIRouter(prefix="/reservations", tags=["inquiry"])


@router.get(
    "/{reservation_id}",
    response_model=ReservationDetailResponse,
    operation_id="get_reservation_by_id",
    responses={404: {"model": ErrorResponse, "description": "該当する予約が存在しない"}},
)
def get_reservation_by_id(reservation_id: str) -> ReservationDetailResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get(
    "",
    response_model=ReservationDetailResponse,
    operation_id="search_reservation_by_guest",
    responses={404: {"model": ErrorResponse, "description": "該当する予約が存在しない"}},
)
def search_reservation_by_guest(
    query: Annotated[ReservationInquiryQuery, Query()],
) -> ReservationDetailResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
