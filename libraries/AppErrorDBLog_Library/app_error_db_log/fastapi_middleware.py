"""FastAPI middleware integration."""

from __future__ import annotations

from typing import Any

from app_error_db_log.logger import AppErrorLogger


class AppErrorDBLogMiddleware:
    """ASGI/FastAPI middleware that logs request exceptions."""

    def __init__(self, app: Any, logger: AppErrorLogger) -> None:
        self.app = app
        self.logger = logger

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        try:
            await self.app(scope, receive, send)
        except Exception as exc:
            headers = dict(scope.get("headers", []))
            client = scope.get("client") or (None, None)
            await self.logger.log_exception_async(
                exc,
                module_name="FastAPI",
                request_path=str(scope.get("path") or ""),
                correlation_id=_decode_header(headers.get(b"x-correlation-id")),
                ip_address=str(client[0]) if client[0] else None,
            )
            if self.logger.config.suppress_original_exception:
                return
            raise


def _decode_header(value: bytes | None) -> str | None:
    if value is None:
        return None
    return value.decode("utf-8", errors="replace")

