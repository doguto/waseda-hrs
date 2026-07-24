"""料金に関するドメインモデル(09の RoomRate / ServiceUsage / Charge)。
金額は円(整数)で扱う。料金計算の業務ルールをここに集約する。"""

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import date


class RoomRateNotConfigured(Exception):
    """客室タイプに対する料金表が未設定のときに送出する。"""


@dataclass(frozen=True)
class RoomRate:
    room_type: str
    price_per_night: int

    def cost_for_nights(self, nights: int) -> int:
        """宿泊料金 = 1泊単価 × 泊数(09の RoomRate.単価を取得する() を計算に使う)。"""
        return self.price_per_night * nights


@dataclass(frozen=True)
class ServiceUsage:
    service_name: str
    fee: int


@dataclass(frozen=True)
class Charge:
    amount: int
    issued_date: date
    paid: bool


def calculate_amount(
    room_rate: RoomRate, nights: int, services: Iterable[ServiceUsage]
) -> int:
    """請求額 = 宿泊料金 + 追加サービス料金の合計。"""
    return room_rate.cost_for_nights(nights) + sum(s.fee for s in services)
