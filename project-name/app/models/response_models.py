from typing import Any

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Any = None
    correlation_id: str | None = None


class StandardResponse(BaseModel):
    success: bool
    message: str
    data: Any = None
    error: ErrorDetail | None = None


class CustomerResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    phone: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
