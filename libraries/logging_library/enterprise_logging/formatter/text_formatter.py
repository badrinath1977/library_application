from __future__ import annotations

import dataclasses
import json

from libraries.logging_library.enterprise_logging.core.types import LogLevel, LogRecord

COLORS = {
    LogLevel.TRACE: "\033[37m",
    LogLevel.DEBUG: "\033[36m",
    LogLevel.INFO: "\033[32m",
    LogLevel.WARN: "\033[33m",
    LogLevel.ERROR: "\033[31m",
    LogLevel.FATAL: "\033[35m",
}
RESET = "\033[0m"


class TextFormatter:
    def __init__(self, *, colorize: bool = False) -> None:
        self.colorize = colorize

    def format(self, record: LogRecord) -> str:
        timestamp = record.timestamp.isoformat()
        correlation = f" correlationId={record.correlation_id}" if record.correlation_id else ""
        module = f" module={record.module}" if record.module else ""
        metadata = (
            f" metadata={json.dumps(record.metadata, default=str)}"
            if record.metadata
            else ""
        )
        context = f" context={json.dumps(record.context, default=str)}" if record.context else ""
        error = ""
        if record.error:
            error_dict = dataclasses.asdict(record.error)
            error = f" error={json.dumps(error_dict, default=str)}"
        line = (
            f"{timestamp} {record.level.name:<5} {record.application}/{record.service}"
            f"{module}{correlation} - {record.message}{metadata}{context}{error}"
        )
        if self.colorize:
            return f"{COLORS.get(record.level, '')}{line}{RESET}"
        return line
