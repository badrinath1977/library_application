from __future__ import annotations

import sys

from libraries.logging_library.enterprise_logging.core.types import LogLevel, LogRecord


class ConsoleTransport:
    name = "console"

    def emit(self, payload: str, record: LogRecord) -> None:
        stream = sys.stderr if record.level >= LogLevel.ERROR else sys.stdout
        print(payload, file=stream, flush=False)

    def flush(self) -> None:
        sys.stdout.flush()
        sys.stderr.flush()

    def close(self) -> None:
        self.flush()
