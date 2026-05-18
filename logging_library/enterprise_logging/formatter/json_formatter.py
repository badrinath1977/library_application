from __future__ import annotations

import dataclasses
import json

from enterprise_logging.core.types import LogRecord


class JsonFormatter:
    def __init__(self, *, timestamp_format: str = "iso8601") -> None:
        self.timestamp_format = timestamp_format

    def format(self, record: LogRecord) -> str:
        payload = {
            "timestamp": record.timestamp.isoformat(),
            "level": record.level.name,
            "message": record.message,
            "module": record.module,
            "correlationId": record.correlation_id,
            "requestId": record.request_id,
            "application": record.application,
            "environment": record.environment,
            "service": record.service,
            "hostname": record.hostname,
            "processId": record.process_id,
            "threadId": record.thread_id,
            "version": record.version,
            "metadata": record.metadata,
            "context": record.context,
            "error": dataclasses.asdict(record.error) if record.error else None,
        }
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"), default=str)
