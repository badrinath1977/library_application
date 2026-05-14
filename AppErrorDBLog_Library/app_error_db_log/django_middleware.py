"""Django middleware integration."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app_error_db_log.logger import AppErrorLogger


class AppErrorDBLogDjangoMiddleware:
    """Django middleware that logs exceptions."""

    def __init__(
        self,
        get_response: Callable[[Any], Any],
        logger: AppErrorLogger | None = None,
    ) -> None:
        self.get_response = get_response
        self.logger = logger

    def __call__(self, request: Any) -> Any:
        try:
            return self.get_response(request)
        except Exception as exc:
            if self.logger is not None:
                self.logger.log_exception(
                    exc,
                    module_name="Django",
                    request_path=getattr(request, "path", None),
                    request_payload=_body_preview(request),
                    ip_address=_client_ip(request),
                )
                if self.logger.config.suppress_original_exception:
                    return None
            raise


def _body_preview(request: Any) -> str | None:
    body = getattr(request, "body", None)
    if body is None:
        return None
    if isinstance(body, bytes):
        return body[:4096].decode("utf-8", errors="replace")
    return str(body)[:4096]


def _client_ip(request: Any) -> str | None:
    meta = getattr(request, "META", {})
    if not isinstance(meta, dict):
        return None
    forwarded_for = meta.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return str(forwarded_for).split(",")[0].strip()
    remote_addr = meta.get("REMOTE_ADDR")
    return str(remote_addr) if remote_addr else None

