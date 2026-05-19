from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.services.absence_service import AbsenceSearchFailed


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _response(request, 422, "VALIDATION_ERROR", "Request validation failed.")

    @app.exception_handler(AbsenceSearchFailed)
    async def absence_search_handler(request: Request, exc: AbsenceSearchFailed) -> JSONResponse:
        return _response(request, 500, "ABSENCE_SEARCH_FAILED", str(exc))

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        return _response(request, 500, "INTERNAL_SERVER_ERROR", "An unexpected error occurred.")


def _response(request: Request, status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "traceId": getattr(request.state, "trace_id", ""),
            "error": {"code": code, "message": message},
        },
    )

