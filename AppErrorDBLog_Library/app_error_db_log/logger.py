"""SQL Server backed application error logger."""

from __future__ import annotations

import asyncio
import json
import threading
import traceback
from collections.abc import Callable
from datetime import UTC, datetime
from functools import wraps
from pathlib import Path
from types import TracebackType
from typing import Any, ParamSpec, TypeVar

from app_error_db_log.config import AppErrorLogConfig
from app_error_db_log.fallback import FallbackFileLogger
from app_error_db_log.models import ErrorLogEntry, LogResult
from app_error_db_log.sql_builder import (
    build_insert_sql,
    build_stored_procedure_sql,
    entry_to_parameters,
)

P = ParamSpec("P")
R = TypeVar("R")


class AppErrorLogger:
    """Thread-safe SQL Server error logger with fallback file support."""

    def __init__(
        self,
        config: AppErrorLogConfig,
        connection_factory: Callable[..., Any] | None = None,
    ) -> None:
        self.config = config
        self._connection_factory = (
            connection_factory or self._default_connection_factory
        )
        self._fallback = FallbackFileLogger(config.fallback_file_path)
        self._lock = threading.RLock()

    @classmethod
    def from_config_file(
        cls,
        config_path: str | Path,
        section: str = "AppErrorDBLog",
    ) -> AppErrorLogger:
        """Create logger from JSON/YAML config file."""

        return cls(AppErrorLogConfig.from_file(config_path, section=section))

    @classmethod
    def from_env(cls, prefix: str = "APP_ERROR_DB_") -> AppErrorLogger:
        """Create logger from environment variables."""

        return cls(AppErrorLogConfig.from_env(prefix=prefix))

    def log_exception(
        self,
        exception: BaseException,
        *,
        module_name: str | None = None,
        correlation_id: str | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
        error_code: str | None = None,
        request_path: str | None = None,
        request_payload: Any | None = None,
        additional_info: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ) -> LogResult:
        """Log an exception to SQL Server or fallback file.

        This method never raises when ``suppress_logger_errors`` is true.
        """

        entry = self._create_entry(
            exception,
            module_name=module_name,
            correlation_id=correlation_id,
            session_id=session_id,
            user_id=user_id,
            error_code=error_code,
            request_path=request_path,
            request_payload=request_payload,
            additional_info=additional_info,
            ip_address=ip_address,
        )
        return self.log_entry(entry)

    def log_entry(self, entry: ErrorLogEntry) -> LogResult:
        """Log a prepared entry."""

        try:
            return self._write_with_retries(entry)
        except Exception as exc:  # noqa: BLE001
            try:
                self._fallback.write(entry, exc)
                result = LogResult(
                    success=False,
                    used_fallback=True,
                    error_message=str(exc),
                    attempts=self.config.retry_count + 1,
                )
            except Exception:
                result = LogResult(
                    success=False,
                    used_fallback=False,
                    error_message=str(exc),
                    attempts=self.config.retry_count + 1,
                )
            if self.config.suppress_logger_errors:
                return result
            raise

    async def log_exception_async(
        self,
        exception: BaseException,
        **kwargs: Any,
    ) -> LogResult:
        """Asynchronously log an exception using a worker thread."""

        return await asyncio.to_thread(self.log_exception, exception, **kwargs)

    def log_exceptions(
        self,
        *,
        module_name: str | None = None,
        suppress_exception: bool | None = None,
    ) -> Callable[[Callable[P, R]], Callable[P, R | None]]:
        """Decorator that logs exceptions from a function."""

        def decorator(func: Callable[P, R]) -> Callable[P, R | None]:
            @wraps(func)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R | None:
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    self.log_exception(exc, module_name=module_name or func.__module__)
                    should_suppress = (
                        suppress_exception
                        if suppress_exception is not None
                        else self.config.suppress_original_exception
                    )
                    if should_suppress:
                        return None
                    raise

            return wrapper

        return decorator

    def capture(
        self,
        *,
        module_name: str | None = None,
        suppress_exception: bool | None = None,
    ) -> ErrorLogContext:
        """Return a context manager that logs exceptions."""

        return ErrorLogContext(
            self,
            module_name=module_name,
            suppress_exception=suppress_exception,
        )

    def _write_with_retries(self, entry: ErrorLogEntry) -> LogResult:
        attempts = self.config.retry_count + 1
        last_error: Exception | None = None
        for attempt in range(1, attempts + 1):
            try:
                self._write_to_database(entry)
                return LogResult(success=True, attempts=attempt)
            except Exception as exc:  # noqa: BLE001
                last_error = exc
        raise RuntimeError("Database error logging failed.") from last_error

    def _write_to_database(self, entry: ErrorLogEntry) -> None:
        if not self.config.connection_string:
            raise ValueError("SQL Server connection string is required.")
        sql = (
            build_stored_procedure_sql(self.config)
            if self.config.stored_procedure_name
            else build_insert_sql(self.config)
        )
        params = entry_to_parameters(entry)
        with self._lock:
            connection = self._connection_factory(
                self.config.connection_string,
                timeout=self.config.timeout_seconds,
            )
            try:
                cursor = connection.cursor()
                cursor.execute(sql, params)
                connection.commit()
            finally:
                connection.close()

    def _default_connection_factory(self, connection_string: str, timeout: int) -> Any:
        try:
            import pyodbc  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError("pyodbc is required for SQL Server logging.") from exc
        return pyodbc.connect(connection_string, timeout=timeout)

    def _create_entry(
        self,
        exception: BaseException,
        *,
        module_name: str | None,
        correlation_id: str | None,
        session_id: str | None,
        user_id: str | None,
        error_code: str | None,
        request_path: str | None,
        request_payload: Any | None,
        additional_info: dict[str, Any] | None,
        ip_address: str | None,
    ) -> ErrorLogEntry:
        return ErrorLogEntry(
            correlation_id=correlation_id,
            session_id=session_id,
            user_id=user_id,
            application_name=self.config.application_name,
            module_name=module_name,
            error_type=exception.__class__.__name__,
            error_code=error_code,
            error_message=str(exception),
            stack_trace="".join(
                traceback.format_exception(
                    type(exception),
                    exception,
                    exception.__traceback__,
                )
            ),
            request_path=request_path,
            request_payload=_safe_json(request_payload),
            additional_info_json=_safe_json(additional_info),
            ip_address=ip_address,
            created_date=datetime.now(UTC),
        )


class ErrorLogContext:
    """Context manager for automatic exception logging."""

    def __init__(
        self,
        logger: AppErrorLogger,
        *,
        module_name: str | None,
        suppress_exception: bool | None,
    ) -> None:
        self._logger = logger
        self._module_name = module_name
        self._suppress_exception = suppress_exception

    def __enter__(self) -> ErrorLogContext:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback_obj: TracebackType | None,
    ) -> bool:
        if exc_value is None:
            return False
        self._logger.log_exception(exc_value, module_name=self._module_name)
        return (
            self._suppress_exception
            if self._suppress_exception is not None
            else self._logger.config.suppress_original_exception
        )


def _safe_json(value: Any | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value
    try:
        return json.dumps(value, default=str)
    except (TypeError, ValueError):
        return str(value)
