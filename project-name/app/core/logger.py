import json
import logging
import sys
from typing import Any

from app.core.config import get_settings
from app.utils.pii_utils import mask_pii


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "service": get_settings().service_name,
        }

        for key in (
            "method",
            "path",
            "status_code",
            "duration_ms",
            "correlation_id",
            "error_code",
            "details",
            "query_params",
            "user",
        ):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = mask_pii(value)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def get_app_logger(name: str | None = None) -> logging.Logger:
    settings = get_settings()
    logger_name = name or settings.service_name
    logger = logging.getLogger(logger_name)
    logger.setLevel(settings.log_level.upper())
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    return logger


def log_exception(
    *,
    exc: Exception,
    status_code: int,
    error_code: str,
    correlation_id: str | None,
    path: str,
    method: str,
    details: Any = None,
) -> None:
    logger = get_app_logger()
    logger.error(
        str(exc),
        exc_info=True,
        extra={
            "status_code": status_code,
            "error_code": error_code,
            "correlation_id": correlation_id,
            "path": path,
            "method": method,
            "details": details,
        },
    )
