from pydantic import BaseModel


class RoomSummary(BaseModel):
    room_number: str
    room_type: str


class RoomSearchResponse(BaseModel):
    rooms: list[RoomSummary]
