"""FastAPIのdependency provider。EngineからControlを組み立てる。"""

from libs.application.inquiry import InquiryControl
from libs.infrastructure.db import get_engine


def get_inquiry_control() -> InquiryControl:
    return InquiryControl(get_engine())
