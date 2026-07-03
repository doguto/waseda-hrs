from fastapi import APIRouter, HTTPException, status

from schemas.response.cancellation import CancellationResponse
from schemas.response.error import ErrorResponse

router = APIRouter(prefix="/reservations", tags=["cancellation"])


@router.post(
    "/{reservation_id}/cancel",
    response_model=CancellationResponse,
    operation_id="cancel_reservation",
    responses={
        404: {"model": ErrorResponse, "description": "該当する予約が存在しない"},
        409: {
            "model": ErrorResponse,
            "description": "予約済み状態でないためキャンセル不可(チェックイン済み等)",
        },
    },
)
def cancel_reservation(reservation_id: str) -> CancellationResponse:
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
