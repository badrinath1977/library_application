from __future__ import annotations

from uuid import uuid4

from enterprise_logging.context.correlation import request_context
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class CorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        trace_id = request.headers.get("X-Trace-ID") or request.headers.get("X-Correlation-ID") or str(uuid4())
        request.state.trace_id = trace_id
        with request_context(correlation_id=trace_id, request_id=request.headers.get("X-Request-ID"), path=request.url.path):
            response = await call_next(request)
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Correlation-ID"] = trace_id
        return response

