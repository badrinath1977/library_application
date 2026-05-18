from __future__ import annotations

import gzip
import shutil
from logging.handlers import RotatingFileHandler
from pathlib import Path

from enterprise_logging.config.schema import RollingPolicy
from enterprise_logging.core.types import LogRecord


class RollingFileTransport:
    name = "file"

    def __init__(self, path: str, policy: RollingPolicy) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._compression = policy.compression
        self._handler = RotatingFileHandler(
            path,
            maxBytes=policy.max_bytes,
            backupCount=policy.backup_count,
            encoding="utf-8",
        )
        if policy.compression:
            self._handler.rotator = self._rotator
            self._handler.namer = lambda name: f"{name}.gz"

    def emit(self, payload: str, record: LogRecord) -> None:
        del record
        line = f"{payload}\n"
        self._handler.acquire()
        try:
            if self._handler.stream is None:
                self._handler.stream = self._handler._open()
            stream = self._handler.stream
            if self._handler.maxBytes > 0:
                stream.seek(0, 2)
                next_size = stream.tell() + len(line.encode("utf-8"))
                if next_size >= self._handler.maxBytes:
                    self._handler.doRollover()
                    if self._handler.stream is None:
                        self._handler.stream = self._handler._open()
                    stream = self._handler.stream
            stream.write(line)
            self._handler.flush()
        finally:
            self._handler.release()

    def flush(self) -> None:
        self._handler.flush()

    def close(self) -> None:
        self._handler.close()

    @staticmethod
    def _rotator(source: str, dest: str) -> None:
        with open(source, "rb") as source_file, gzip.open(dest, "wb") as dest_file:
            shutil.copyfileobj(source_file, dest_file)
        Path(source).unlink(missing_ok=True)
