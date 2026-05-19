"""Flask integration helpers."""

from __future__ import annotations

from typing import Any

from app_error_db_log.logger import AppErrorLogger


def register_flask_error_handler(app: Any, logger: AppErrorLogger) -> None:
    """Register a Flask error handler that logs exceptions."""

    def _handle_exception(error: Exception) -> Any:
        try:
            from flask import request  # type: ignore[import-not-found]
        except ImportError:
            request = None
        logger.log_exception(
            error,
            module_name="Flask",
            request_path=getattr(request, "path", None),
            request_payload=_safe_request_payload(request),
            ip_address=getattr(request, "remote_addr", None),
        )
        if logger.config.suppress_original_exception:
            return "Internal Server Error", 500
        raise error

    app.register_error_handler(Exception, _handle_exception)


def _safe_request_payload(request: Any) -> Any | None:
    if request is None:
        return None
    try:
        return request.get_json(silent=True)
    except Exception:  # noqa: BLE001
        return None
