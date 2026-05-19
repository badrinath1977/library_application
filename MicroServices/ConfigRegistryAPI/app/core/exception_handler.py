from __future__ import annotations

from typing import Any

from app_error_db_log import AppErrorLogConfig, AppErrorLogger
from enterprise_logging import get_logger
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.errors import ConfigRegistryError
from app.core.settings import Settings
from app.services.security import protect_log_payload


def create_app_error_logger(settings: Settings) -> AppErrorLogger:
    return AppErrorLogger(
        AppErrorLogConfig(
            connection_string="",
            application_name=settings.app_name,
            fallback_file_path=settings.app_error_fallback_file,
            suppress_logger_errors=True,
        )
    )


def register_exception_handlers(app: FastAPI, settings: Settings) -> None:
    logger = get_logger("core.exceptions")
    db_error_logger = create_app_error_logger(settings)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        return _error_response(request, exc.status_code, "http_error", str(exc.detail))

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        logger.warn(
            "request.validation_failed",
            protect_log_payload({"errors": exc.errors(), "path": request.url.path}, _cid(request)),
        )
        return _error_response(request, 422, "validation_error", "Request validation failed")

    @app.exception_handler(ConfigRegistryError)
    async def registry_exception_handler(
        request: Request,
        exc: ConfigRegistryError,
    ) -> JSONResponse:
        await _log_exception(db_error_logger, logger, request, exc, exc.error_code)
        return _error_response(request, exc.status_code, exc.error_code, str(exc))

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        await _log_exception(db_error_logger, logger, request, exc, "unhandled_exception")
        return _error_response(
            request,
            500,
            "internal_server_error",
            "An unexpected error occurred.",
        )


async def _log_exception(
    db_error_logger: AppErrorLogger,
    logger: Any,
    request: Request,
    exc: Exception,
    error_code: str,
) -> None:
    correlation_id = _cid(request)
    logger.error(
        "request.failed",
        exc,
        protect_log_payload(
            {
                "path": request.url.path,
                "method": request.method,
                "errorCode": error_code,
            },
            correlation_id,
        ),
    )
    await db_error_logger.log_exception_async(
        exc,
        module_name="ConfigRegistryAPI",
        correlation_id=correlation_id,
        error_code=error_code,
        request_path=request.url.path,
        request_payload={"method": request.method},
        additional_info={"service": "ConfigRegistryAPI"},
        ip_address=request.client.host if request.client else None,
    )


def _error_response(request: Request, status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "correlationId": _cid(request),
            "error": {"code": code, "message": message},
        },
    )


def _cid(request: Request) -> str:
    return getattr(request.state, "correlation_id", "")
