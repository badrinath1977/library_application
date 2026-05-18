from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import IntEnum
from typing import Any


class LogLevel(IntEnum):
    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARN = 30
    ERROR = 40
    FATAL = 50

    @classmethod
    def parse(cls, value: str | int | LogLevel) -> LogLevel:
        if isinstance(value, cls):
            return value
        if isinstance(value, int):
            for level in cls:
                if int(level) == value:
                    return level
        normalized = str(value).upper()
        if normalized == "WARNING":
            normalized = "WARN"
        try:
            return cls[normalized]
        except KeyError as exc:
            supported = ", ".join(level.name for level in cls)
            raise ValueError(
                f"Unsupported log level {value!r}. Supported levels: {supported}"
            ) from exc


@dataclass(frozen=True, slots=True)
class ErrorInfo:
    type: str
    message: str
    stack: str | None = None
    cause: ErrorInfo | None = None
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class LogRecord:
    timestamp: datetime
    level: LogLevel
    message: str
    module: str | None
    application: str
    environment: str
    service: str
    hostname: str
    process_id: int
    thread_id: int
    correlation_id: str | None = None
    request_id: str | None = None
    version: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)
    error: ErrorInfo | None = None

    @classmethod
    def create(
        cls,
        *,
        level: LogLevel,
        message: str,
        module: str | None,
        application: str,
        environment: str,
        service: str,
        hostname: str,
        process_id: int,
        thread_id: int,
        correlation_id: str | None,
        request_id: str | None,
        version: str | None,
        metadata: dict[str, Any],
        context: dict[str, Any],
        error: ErrorInfo | None,
    ) -> LogRecord:
        return cls(
            timestamp=datetime.now(UTC),
            level=level,
            message=message,
            module=module,
            application=application,
            environment=environment,
            service=service,
            hostname=hostname,
            process_id=process_id,
            thread_id=thread_id,
            correlation_id=correlation_id,
            request_id=request_id,
            version=version,
            metadata=metadata,
            context=context,
            error=error,
        )
