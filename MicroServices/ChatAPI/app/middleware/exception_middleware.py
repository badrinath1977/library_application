from __future__ import annotations

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        try:
            return await call_next(request)
        except HTTPException as exc:
            return self._response(request, exc.status_code, "http_error", str(exc.detail))
        except RequestValidationError:
            return self._response(request, 422, "validation_error", "Request validation failed.")
        except Exception:
            return self._response(request, 500, "internal_server_error", "An unexpected error occurred.")

    @staticmethod
    def _response(request: Request, status_code: int, code: str, message: str) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "traceId": getattr(request.state, "trace_id", ""),
                "error": {"code": code, "message": message},
            },
        )

