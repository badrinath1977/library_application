from __future__ import annotations

from typing import Any

from enterprise_logging.core.logger import Logger


def log_api_error(
    logger: Logger,
    *,
    message: str,
    error: BaseException,
    status_code: int,
    method: str | None = None,
    path: str | None = None,
    response_body: Any = None,
) -> None:
    logger.error(
        message,
        error,
        {
            "statusCode": status_code,
            "method": method,
            "path": path,
            "responseBody": response_body,
        },
    )
