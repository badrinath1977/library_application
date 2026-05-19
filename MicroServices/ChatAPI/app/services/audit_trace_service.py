from __future__ import annotations

import time
from typing import Any

from app_error_db_log import AppErrorLogConfig, AppErrorLogger
from enterprise_logging import get_logger

from app.core.settings import Settings
from app.services.pii_security_service import mask_for_log


class AuditTraceService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._logger = get_logger("services.audit_trace")
        self._error_logger = AppErrorLogger(
            AppErrorLogConfig(
                connection_string="",
                application_name=settings.app_name,
                fallback_file_path=settings.app_error_fallback_file,
                suppress_logger_errors=True,
            )
        )

    def mark(self) -> float:
        return time.perf_counter()

    def elapsed_ms(self, started: float) -> int:
        return int((time.perf_counter() - started) * 1000)

    def event(self, trace_id: str, name: str, data: dict[str, Any] | None = None) -> None:
        self._logger.info(
            f"chat.{name}",
            mask_for_log({"traceId": trace_id, **(data or {})}, trace_id),
        )

    async def error(
        self,
        trace_id: str,
        exc: Exception,
        *,
        request_path: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> None:
        self._logger.error(
            "chat.error",
            exc,
            mask_for_log({"traceId": trace_id, **(data or {})}, trace_id),
        )
        await self._error_logger.log_exception_async(
            exc,
            module_name="ChatAPI",
            correlation_id=trace_id,
            error_code=exc.__class__.__name__,
            request_path=request_path,
            request_payload=mask_for_log(data or {}, trace_id),
            additional_info={"service": self._settings.service_name},
        )

