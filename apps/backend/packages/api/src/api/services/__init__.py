"""FastAPIのdependency provider。UnitOfWorkからControlを組み立てる。

具象の UnitOfWork(SQLAlchemy実装)を選ぶのはこの合成の場所だけで、
Control 自身は `libs.domain.repositories.UnitOfWork` にのみ依存する。
"""

from libs.application.cancellation import CancellationControl
from libs.application.catalog import CatalogControl
from libs.application.checkin import CheckInControl
from libs.application.checkout import CheckOutControl
from libs.application.inquiry import InquiryControl
from libs.application.reservation import ReservationControl
from libs.domain.repositories import UnitOfWork
from libs.infrastructure.db import get_engine
from libs.infrastructure.db.unit_of_work import SqlAlchemyUnitOfWork


def get_unit_of_work() -> UnitOfWork:
    return SqlAlchemyUnitOfWork(get_engine())


def get_inquiry_control() -> InquiryControl:
    return InquiryControl(get_unit_of_work())


def get_catalog_control() -> CatalogControl:
    return CatalogControl(get_unit_of_work())


def get_reservation_control() -> ReservationControl:
    return ReservationControl(get_unit_of_work())


def get_check_out_control() -> CheckOutControl:
    return CheckOutControl(get_unit_of_work())


def get_cancellation_control() -> CancellationControl:
    return CancellationControl(get_unit_of_work())


def get_check_in_control() -> CheckInControl:
    return CheckInControl(get_unit_of_work())
