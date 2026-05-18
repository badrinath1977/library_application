from __future__ import annotations

import time
from collections.abc import Awaitable, Callable
from typing import Any
from uuid import uuid4

from enterprise_logging import get_logger
from enterprise_logging.context.correlation import request_context

Receive = Callable[[], Awaitable[dict[str, Any]]]
Send = Callable[[dict[str, Any]], Awaitable[None]]
ASGIApp = Callable[[dict[str, Any], Receive, Send], Awaitable[None]]


class CorrelationASGIMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        *,
        header_name: str = "x-correlation-id",
        module_name: str = "http",
    ) -> None:
        self.app = app
        self.header_name = header_name.lower().encode("latin-1")
        self.logger = get_logger(module_name)

    async def __call__(
        self,
        scope: dict[str, Any],
        receive: Receive,
        send: Send,
    ) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return
        headers = dict(scope.get("headers", []))
        correlation_id = headers.get(
            self.header_name,
            str(uuid4()).encode("latin-1"),
        ).decode("latin-1")
        started = time.perf_counter()
        status_code = 500

        async def send_wrapper(message: dict[str, Any]) -> None:
            nonlocal status_code
            if message.get("type") == "http.response.start":
                status_code = int(message.get("status", 500))
                response_headers = list(message.get("headers", []))
                response_headers.append((self.header_name, correlation_id.encode("latin-1")))
                message["headers"] = response_headers
            await send(message)

        with request_context(
            correlation_id=correlation_id,
            method=scope.get("method"),
            path=scope.get("path"),
            client=scope.get("client"),
        ):
            self.logger.info("request.started")
            try:
                await self.app(scope, receive, send_wrapper)
            except Exception as exc:
                latency_ms = round((time.perf_counter() - started) * 1000, 2)
                self.logger.error("request.failed", exc, {"latencyMs": latency_ms})
                raise
            latency_ms = round((time.perf_counter() - started) * 1000, 2)
            self.logger.info(
                "request.completed",
                {"statusCode": status_code, "latencyMs": latency_ms},
            )
