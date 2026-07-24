"""FastAPIのdependency provider。EngineからControlを組み立てる。"""

from libs.application.cancellation import CancellationControl
from libs.application.inquiry import InquiryControl
from libs.infrastructure.db import get_engine


def get_inquiry_control() -> InquiryControl:
    return InquiryControl(get_engine())


def get_cancellation_control() -> CancellationControl:
    return CancellationControl(get_engine())
