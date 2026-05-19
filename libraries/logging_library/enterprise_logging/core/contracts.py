from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from libraries.logging_library.enterprise_logging.core.types import LogRecord


@runtime_checkable
class Formatter(Protocol):
    def format(self, record: LogRecord) -> str:
        """Convert a log record into a transport payload."""


@runtime_checkable
class Transport(Protocol):
    name: str

    def emit(self, payload: str, record: LogRecord) -> None:
        """Write one formatted log event."""

    def flush(self) -> None:
        """Flush buffered events."""

    def close(self) -> None:
        """Release resources."""


@runtime_checkable
class Masker(Protocol):
    def mask(self, value: Any) -> Any:
        """Return an immutable, serialization-safe, masked representation."""


@runtime_checkable
class Serializer(Protocol):
    def serialize(self, value: Any) -> Any:
        """Convert arbitrary values into JSON-safe values."""
