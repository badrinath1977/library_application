import time

from fastapi import Request

from app.core.logger import get_app_logger
from app.utils.pii_utils import mask_pii


async def request_response_logging_middleware(request: Request, call_next):
    logger = get_app_logger()
    start_time = time.perf_counter()
    correlation_id = getattr(request.state, "correlation_id", None)

    logger.info(
        "Request started",
        extra={
            "method": request.method,
            "path": request.url.path,
            "correlation_id": correlation_id,
            "query_params": mask_pii(dict(request.query_params)),
        },
    )

    response = await call_next(request)
    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
    correlation_id = getattr(request.state, "correlation_id", correlation_id)

    logger.info(
        "Request completed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "correlation_id": correlation_id,
        },
    )
    return response
