from datetime import date

from pydantic import BaseModel, Field, model_validator


class RoomSearchQuery(BaseModel):
    check_in_date: date
    check_out_date: date
    room_type: str | None = Field(default=None, description="未指定なら全タイプを検索")

    @model_validator(mode="after")
    def check_date_order(self) -> "RoomSearchQuery":
        if self.check_out_date <= self.check_in_date:
            raise ValueError("check_out_date must be after check_in_date")
        return self
