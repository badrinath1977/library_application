from __future__ import annotations


class LoggingConfigurationError(ValueError):
    """Raised when logging configuration is invalid."""


class TransportEmitError(RuntimeError):
    """Raised when a transport cannot emit and fail-fast mode is enabled."""
