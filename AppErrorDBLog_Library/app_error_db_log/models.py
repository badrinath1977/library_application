"""Data models for application error logging."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class ErrorLogEntry:
    """Structured error log payload persisted to SQL Server."""

    correlation_id: str | None = None
    session_id: str | None = None
    user_id: str | None = None
    application_name: str | None = None
    module_name: str | None = None
    error_type: str | None = None
    error_code: str | None = None
    error_message: str | None = None
    stack_trace: str | None = None
    request_path: str | None = None
    request_payload: str | None = None
    additional_info_json: str | None = None
    ip_address: str | None = None
    created_date: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass(frozen=True, slots=True)
class LogResult:
    """Result of an attempted logging operation."""

    success: bool
    used_fallback: bool = False
    error_message: str | None = None
    attempts: int = 0


JsonObject = dict[str, Any]

