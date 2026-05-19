from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass

from libraries.logging_library.enterprise_logging.config.schema import AsyncConfig
from libraries.logging_library.enterprise_logging.core.contracts import Formatter, Transport
from libraries.logging_library.enterprise_logging.core.exceptions import TransportEmitError
from libraries.logging_library.enterprise_logging.core.types import LogRecord


@dataclass(frozen=True, slots=True)
class _Envelope:
    record: LogRecord


class AsyncDispatcher:
    def __init__(
        self,
        *,
        transports: tuple[tuple[Transport, Formatter], ...],
        config: AsyncConfig,
    ) -> None:
        self._transports = transports
        self._config = config
        self._queue: queue.Queue[_Envelope | None] = queue.Queue(maxsize=config.queue_size)
        self._closed = threading.Event()
        self._worker = threading.Thread(
            target=self._run,
            name="enterprise-logging-dispatcher",
            daemon=True,
        )
        self._worker.start()

    def emit(self, record: LogRecord) -> None:
        envelope = _Envelope(record)
        try:
            if self._config.drop_when_full:
                self._queue.put_nowait(envelope)
            else:
                self._queue.put(envelope, timeout=0.25)
        except queue.Full as exc:
            if self._config.fail_fast:
                raise TransportEmitError("Logging queue is full") from exc

    def flush(self) -> None:
        self._queue.join()
        for transport, _formatter in self._transports:
            transport.flush()

    def close(self) -> None:
        if self._closed.is_set():
            return
        self.flush()
        self._closed.set()
        self._queue.put(None)
        self._worker.join(timeout=5)
        for transport, _formatter in self._transports:
            transport.close()

    def _run(self) -> None:
        batch: list[_Envelope] = []
        last_flush = time.monotonic()
        while True:
            timeout = max(0.001, self._config.flush_interval_seconds)
            try:
                item = self._queue.get(timeout=timeout)
            except queue.Empty:
                item = None
            if item is None:
                self._drain_batch(batch)
                batch.clear()
                if self._closed.is_set():
                    self._queue.task_done()
                    return
                last_flush = time.monotonic()
                continue
            batch.append(item)
            now = time.monotonic()
            interval_elapsed = now - last_flush >= self._config.flush_interval_seconds
            if len(batch) >= self._config.batch_size or interval_elapsed:
                self._drain_batch(batch)
                batch.clear()
                last_flush = now

    def _drain_batch(self, batch: list[_Envelope]) -> None:
        for envelope in batch:
            for transport, formatter in self._transports:
                try:
                    transport.emit(formatter.format(envelope.record), envelope.record)
                except Exception as exc:
                    if self._config.fail_fast:
                        raise TransportEmitError(f"Transport {transport.name} failed") from exc
            self._queue.task_done()
        for transport, _formatter in self._transports:
            transport.flush()
