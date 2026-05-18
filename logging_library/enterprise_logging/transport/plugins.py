from __future__ import annotations

import urllib.error
import urllib.request
from urllib.parse import urlparse

from enterprise_logging.core.exceptions import LoggingConfigurationError, TransportEmitError
from enterprise_logging.core.types import LogRecord


class ProviderHttpTransport:
    """Generic HTTP adapter for centralized logging provider gateways.

    Provider-specific integrations can subclass this or register a custom
    transport factory while preserving the same logging API.
    """

    def __init__(self, name: str, options: dict[str, object]) -> None:
        self.name = name
        self.options = dict(options)
        endpoint = self.options.get("endpoint")
        if not isinstance(endpoint, str) or not endpoint:
            raise LoggingConfigurationError(f"{name} transport requires options.endpoint")
        if urlparse(endpoint).scheme not in {"http", "https"}:
            raise LoggingConfigurationError(f"{name} transport endpoint must use http or https")
        self.endpoint = endpoint
        timeout = self.options.get("timeout_seconds", 2.0)
        if not isinstance(timeout, int | float | str):
            raise LoggingConfigurationError(f"{name} transport timeout_seconds must be numeric")
        self.timeout_seconds = float(timeout)
        headers = self.options.get("headers", {})
        self.headers = dict(headers) if isinstance(headers, dict) else {}
        self.headers.setdefault("content-type", "application/json")

    def emit(self, payload: str, record: LogRecord) -> None:
        del record
        request = urllib.request.Request(  # noqa: S310
            self.endpoint,
            data=payload.encode("utf-8"),
            headers={str(key): str(value) for key, value in self.headers.items()},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:  # noqa: S310
                if response.status >= 400:
                    raise TransportEmitError(
                        f"{self.name} transport returned HTTP {response.status}"
                    )
        except urllib.error.URLError as exc:
            raise TransportEmitError(f"{self.name} transport failed: {exc}") from exc

    def flush(self) -> None:
        pass

    def close(self) -> None:
        self.flush()
