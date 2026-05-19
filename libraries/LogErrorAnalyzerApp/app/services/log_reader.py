"""Safe log file reading."""

from __future__ import annotations

import logging
from pathlib import Path

from libraries.LogErrorAnalyzerApp.app.core.exceptions import LogReadError

logger = logging.getLogger(__name__)


class LogReader:
    """Read log files safely."""

    def __init__(self, max_file_size_mb: int = 25) -> None:
        self._max_bytes = max_file_size_mb * 1024 * 1024

    def read_file(self, path: Path) -> str:
        """Read a log file as text."""

        try:
            if path.stat().st_size > self._max_bytes:
                raise LogReadError(f"File exceeds size limit: {path}")
            content = path.read_text(encoding="utf-8", errors="replace")
        except PermissionError as exc:
            logger.exception("Permission denied while reading log file: %s", path)
            raise LogReadError(f"Permission denied: {path}") from exc
        except OSError as exc:
            logger.exception("Failed to read log file: %s", path)
            raise LogReadError(f"Unable to read file: {path}") from exc
        return content

