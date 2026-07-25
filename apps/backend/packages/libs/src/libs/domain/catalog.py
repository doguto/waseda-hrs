"""部屋タイプの閲覧に使う読み取りモデル。予約前のブラウズ用の集計ビュー。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RoomTypeSummary:
    room_type: str
    price_per_night: int
    vacant_count: int
