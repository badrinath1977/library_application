from __future__ import annotations

from uuid import uuid4

from enterprise_logging.context.correlation import request_context
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class CorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid4())
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        request.state.correlation_id = correlation_id
        request.state.request_id = request_id
        with request_context(
            correlation_id=correlation_id,
            request_id=request_id,
            method=request.method,
            path=request.url.path,
        ):
            response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Request-ID"] = request_id
        return response

