from datetime import date

from pydantic import BaseModel


class ServiceChargeItem(BaseModel):
    service_name: str
    fee: int


class ChargeResponse(BaseModel):
    room_charge: int
    service_charges: list[ServiceChargeItem]
    total: int


class CheckOutResponse(BaseModel):
    reservation_id: str
    amount: int
    paid: bool
    issued_date: date
