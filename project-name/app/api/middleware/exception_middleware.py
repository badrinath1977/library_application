import logging
from typing import Any, Mapping

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.core.error_logging import log_error_to_db
from app.core.exceptions import AppException
from app.core.logger import log_exception
from app.utils.response_builder import build_error_response


def handle_exception(
    request: Request,
    exc: Exception,
    status_code: int,
    error_code: str,
    message: str,
    details: Any = None,
    headers: Mapping[str, str] | None = None,
):
    settings = getattr(request.app.state, "settings", None)
    service_name = getattr(settings, "service_name", "project-name")
    correlation_id = getattr(request.state, "correlation_id", None)
    safe_details = jsonable_encoder(details) if details is not None else None

    try:
        log_exception(
            exc=exc,
            status_code=status_code,
            error_code=error_code,
            correlation_id=correlation_id,
            path=request.url.path,
            method=request.method,
            details=safe_details,
        )
    except Exception:
        logging.getLogger(__name__).exception("Failed to write application error log")

    try:
        log_error_to_db(
            service_name=service_name,
            path=request.url.path,
            method=request.method,
            status_code=status_code,
            error_code=error_code,
            message=str(exc),
            correlation_id=correlation_id,
            details=safe_details,
        )
    except Exception:
        logging.getLogger(__name__).exception("Failed to persist application error")

    return JSONResponse(
        status_code=status_code,
        headers=dict(headers) if headers else None,
        content=build_error_response(
            message=message,
            error_code=error_code,
            details=safe_details,
            correlation_id=correlation_id,
        ),
    )


async def exception_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except AppException as exc:
        return handle_exception(
            request,
            exc,
            exc.status_code,
            exc.error_code,
            exc.message,
            exc.details,
            exc.headers,
        )
    except Exception as exc:
        return handle_exception(request, exc, 500, "INTERNAL_ERROR", "Internal server error")
