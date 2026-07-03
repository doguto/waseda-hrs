from pydantic import BaseModel


class CheckInResponse(BaseModel):
    room_number: str
