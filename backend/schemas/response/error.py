from pydantic import BaseModel, Field

from schemas.common import ErrorCode


class ErrorResponse(BaseModel):
    error_code: ErrorCode
    message: str = Field(examples=["該当する空室がありません"])
