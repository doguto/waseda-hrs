"""FastAPIのdependency provider。EngineからControlを組み立てる。"""

from libs.application.cancellation import CancellationControl
from libs.application.catalog import CatalogControl
from libs.application.checkin import CheckInControl
from libs.application.checkout import CheckOutControl
from libs.application.inquiry import InquiryControl
from libs.application.reservation import ReservationControl
from libs.infrastructure.db import get_engine


def get_inquiry_control() -> InquiryControl:
    return InquiryControl(get_engine())


def get_catalog_control() -> CatalogControl:
    return CatalogControl(get_engine())


def get_reservation_control() -> ReservationControl:
    return ReservationControl(get_engine())


def get_check_out_control() -> CheckOutControl:
    return CheckOutControl(get_engine())


def get_cancellation_control() -> CancellationControl:
    return CancellationControl(get_engine())


def get_check_in_control() -> CheckInControl:
    return CheckInControl(get_engine())
