from __future__ import annotations

import time
from collections.abc import Callable, Iterable
from typing import Any
from uuid import uuid4

from enterprise_logging import get_logger
from enterprise_logging.context.correlation import request_context

StartResponse = Callable[[str, list[tuple[str, str]], Any], Callable[[bytes], Any]]
WSGIApp = Callable[[dict[str, Any], StartResponse], Iterable[bytes]]


class CorrelationWSGIMiddleware:
    def __init__(
        self,
        app: WSGIApp,
        *,
        header_name: str = "X-Correlation-ID",
        module_name: str = "http",
    ) -> None:
        self.app = app
        self.header_name = header_name
        self.environ_key = f"HTTP_{header_name.upper().replace('-', '_')}"
        self.logger = get_logger(module_name)

    def __call__(self, environ: dict[str, Any], start_response: StartResponse) -> Iterable[bytes]:
        correlation_id = str(environ.get(self.environ_key) or uuid4())
        started = time.perf_counter()
        status_holder = {"status": "500 Internal Server Error"}

        def start_response_wrapper(
            status: str,
            headers: list[tuple[str, str]],
            exc_info: Any = None,
        ) -> Callable[[bytes], Any]:
            status_holder["status"] = status
            headers.append((self.header_name, correlation_id))
            return start_response(status, headers, exc_info)

        with request_context(
            correlation_id=correlation_id,
            method=environ.get("REQUEST_METHOD"),
            path=environ.get("PATH_INFO"),
            remoteAddr=environ.get("REMOTE_ADDR"),
        ):
            self.logger.info("request.started")
            try:
                result = self.app(environ, start_response_wrapper)
            except Exception as exc:
                latency_ms = round((time.perf_counter() - started) * 1000, 2)
                self.logger.error("request.failed", exc, {"latencyMs": latency_ms})
                raise
            latency_ms = round((time.perf_counter() - started) * 1000, 2)
            self.logger.info(
                "request.completed",
                {"status": status_holder["status"], "latencyMs": latency_ms},
            )
            return result
