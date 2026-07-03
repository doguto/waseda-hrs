from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from schemas.request.reservation import ReservationCreateRequest
from schemas.request.room import RoomSearchQuery
from schemas.response.error import ErrorResponse
from schemas.response.reservation import ReservationCreateResponse
from schemas.response.room import RoomSearchResponse

router = APIRouter(tags=["reservation"])


@router.get(
    "/rooms/available",
    response_model=RoomSearchResponse,
    operation_id="search_available_rooms",
)
def search_available_rooms(
    query: Annotated[RoomSearchQuery, Query()],
) -> RoomSearchResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.post(
    "/reservations",
    response_model=ReservationCreateResponse,
    status_code=status.HTTP_201_CREATED,
    operation_id="create_reservation",
    responses={
        409: {
            "model": ErrorResponse,
            "description": "客室が直前に他の予約で確保された(予約の競合)",
        }
    },
)
def create_reservation(body: ReservationCreateRequest) -> ReservationCreateResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
