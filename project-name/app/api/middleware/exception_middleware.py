from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.error_logging import log_error_to_db
from app.core.exceptions import AppException
from app.core.logger import log_exception
from app.utils.response_builder import build_error_response


def handle_exception(request: Request, exc: Exception, status_code: int, error_code: str, message: str, details=None):
    settings = getattr(request.app.state, "settings", None)
    service_name = getattr(settings, "service_name", "project-name")
    correlation_id = getattr(request.state, "correlation_id", None)

    log_exception(
        exc=exc,
        status_code=status_code,
        error_code=error_code,
        correlation_id=correlation_id,
        path=request.url.path,
        method=request.method,
        details=details,
    )
    log_error_to_db(
        service_name=service_name,
        path=request.url.path,
        method=request.method,
        status_code=status_code,
        error_code=error_code,
        message=str(exc),
        correlation_id=correlation_id,
        details=details,
    )

    return JSONResponse(
        status_code=status_code,
        content=build_error_response(
            message=message,
            error_code=error_code,
            details=details,
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
        )
    except Exception as exc:
        return handle_exception(request, exc, 500, "INTERNAL_ERROR", "Internal server error")
