from datetime import date

from pydantic import BaseModel, Field, model_validator


class ReservationCreateRequest(BaseModel):
    room_number: str
    check_in_date: date
    check_out_date: date
    guest_name: str = Field(min_length=1)
    guest_contact: str = Field(min_length=1, description="電話番号またはメールアドレス")

    @model_validator(mode="after")
    def check_date_order(self) -> "ReservationCreateRequest":
        if self.check_out_date <= self.check_in_date:
            raise ValueError("check_out_date must be after check_in_date")
        return self


class ReservationInquiryQuery(BaseModel):
    guest_name: str = Field(min_length=1)
    check_in_date: date
