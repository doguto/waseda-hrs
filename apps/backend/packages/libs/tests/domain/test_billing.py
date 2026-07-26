"""料金計算のテスト。UC3 チェックアウトする で使う
「請求額 = 1泊単価 × 泊数 + 追加サービス料金の合計」という業務ルールを確認する。"""

from libs.domain.billing import RoomRate, ServiceUsage, calculate_amount


class TestCostForNights:
    def test_multiplies_price_by_nights(self) -> None:
        """宿泊料金は単価 × 泊数。"""
        rate = RoomRate(room_type="SINGLE", price_per_night=12000)

        assert rate.cost_for_nights(3) == 36000

    def test_single_night(self) -> None:
        """1泊なら単価そのまま。"""
        rate = RoomRate(room_type="SINGLE", price_per_night=12000)

        assert rate.cost_for_nights(1) == 12000


class TestCalculateAmount:
    def test_room_charge_only_without_services(self) -> None:
        """追加サービスがなければ請求額は宿泊料金だけ。"""
        rate = RoomRate(room_type="DOUBLE", price_per_night=20000)

        assert calculate_amount(rate, 2, []) == 40000

    def test_adds_service_fees(self) -> None:
        """追加サービスの料金を宿泊料金に加算する。"""
        rate = RoomRate(room_type="DOUBLE", price_per_night=20000)
        services = [
            ServiceUsage(service_name="朝食", fee=2000),
            ServiceUsage(service_name="ランドリー", fee=1500),
        ]

        assert calculate_amount(rate, 2, services) == 43500

    def test_accepts_iterator_of_services(self) -> None:
        """サービスの引数は Iterable なので、リスト以外のイテレータでも扱える。"""
        rate = RoomRate(room_type="SINGLE", price_per_night=12000)
        services = iter([ServiceUsage(service_name="朝食", fee=2000)])

        assert calculate_amount(rate, 1, services) == 14000

from datetime import date
from libs.domain.billing import Charge

class TestCharge:
    def test_charge_attributes(self) -> None:
        charge = Charge(amount=10000, issued_date=date(2026, 7, 26), paid=False)
        assert charge.amount == 10000
        assert charge.issued_date == date(2026, 7, 26)
        assert charge.paid is False

from datetime import date
from libs.domain.billing import Charge

class TestCharge:
    def test_charge_attributes(self) -> None:
        charge = Charge(amount=10000, issued_date=date(2026, 7, 26), paid=False)
        assert charge.amount == 10000
        assert charge.issued_date == date(2026, 7, 26)
        assert charge.paid is False
