"""部屋タイプ閲覧APIのresponse schema(BCEのboundary)。"""

import pydantic
from libs.domain.catalog import RoomTypeSummary


class RoomTypeResponse(pydantic.BaseModel):
    room_type: str
    price_per_night: int
    vacant_count: int

    @classmethod
    def from_domain(cls, summary: RoomTypeSummary) -> "RoomTypeResponse":
        return cls(
            room_type=summary.room_type,
            price_per_night=summary.price_per_night,
            vacant_count=summary.vacant_count,
        )
