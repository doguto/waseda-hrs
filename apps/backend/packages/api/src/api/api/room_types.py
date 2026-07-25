"""部屋タイプ閲覧のroute(BCEのboundary)。予約前のブラウズ用の読み取りAPI。"""

from fastapi import APIRouter, Depends, HTTPException
from libs.application.catalog import CatalogControl

from api.api.schemas.room_type import RoomTypeResponse
from api.services import get_catalog_control

router = APIRouter(tags=["room-types"])


@router.get("/room-types")
def list_room_types(
    control: CatalogControl = Depends(get_catalog_control),
) -> list[RoomTypeResponse]:
    return [RoomTypeResponse.from_domain(s) for s in control.list_room_types()]


@router.get("/room-types/{room_type}")
def get_room_type(
    room_type: str,
    control: CatalogControl = Depends(get_catalog_control),
) -> RoomTypeResponse:
    summary = control.find_room_type(room_type)
    if summary is None:
        raise HTTPException(status_code=404, detail="room type not found")
    return RoomTypeResponse.from_domain(summary)
