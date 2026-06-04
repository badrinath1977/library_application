from typing import Any
import json
import sqlite3
from datetime import datetime, timezone

from app.core.config import get_settings
from app.core.logger import get_app_logger


def log_error_to_db(
    *,
    service_name: str,
    path: str,
    method: str,
    status_code: int,
    error_code: str,
    message: str,
    correlation_id: str | None,
    details: Any = None,
) -> None:
    settings = get_settings()
    logger = get_app_logger()
    if not settings.error_db_enabled:
        return

    payload = {
        "service_name": service_name,
        "path": path,
        "method": method,
        "status_code": status_code,
        "error_code": error_code,
        "message": message,
        "correlation_id": correlation_id,
        "details": details,
    }

    try:
        with sqlite3.connect(settings.error_db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS application_error_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    service_name TEXT NOT NULL,
                    path TEXT NOT NULL,
                    method TEXT NOT NULL,
                    status_code INTEGER NOT NULL,
                    error_code TEXT NOT NULL,
                    message TEXT NOT NULL,
                    correlation_id TEXT,
                    details TEXT
                )
                """
            )
            connection.execute(
                """
                INSERT INTO application_error_logs (
                    created_at,
                    service_name,
                    path,
                    method,
                    status_code,
                    error_code,
                    message,
                    correlation_id,
                    details
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now(timezone.utc).isoformat(),
                    payload["service_name"],
                    payload["path"],
                    payload["method"],
                    payload["status_code"],
                    payload["error_code"],
                    payload["message"],
                    payload["correlation_id"],
                    json.dumps(payload["details"], default=str),
                ),
            )
            connection.commit()
    except Exception:
        logger.exception("Failed to persist error log")
