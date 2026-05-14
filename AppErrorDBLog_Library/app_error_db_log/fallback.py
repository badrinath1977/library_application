"""Fallback local file logging when SQL logging fails."""

from __future__ import annotations

import json
import threading
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from app_error_db_log.models import ErrorLogEntry


class FallbackFileLogger:
    """Thread-safe fallback logger that writes JSON lines to disk."""

    def __init__(self, fallback_file_path: str) -> None:
        self._path = Path(fallback_file_path)
        self._lock = threading.RLock()

    def write(
        self,
        entry: ErrorLogEntry,
        logger_error: Exception | None = None,
    ) -> None:
        """Write one fallback log line."""

        with self._lock:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            payload = asdict(entry)
            payload["created_date"] = entry.created_date.isoformat()
            payload["fallback_created_utc"] = datetime.utcnow().isoformat()
            if logger_error is not None:
                payload["logger_error"] = str(logger_error)
            with self._path.open("a", encoding="utf-8") as file:
                file.write(json.dumps(payload, default=str) + "\n")
