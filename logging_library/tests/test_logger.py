# ruff: noqa: S105

import json
import threading

from enterprise_logging.config.schema import AsyncConfig, LoggerConfig, OutputConfig
from enterprise_logging.context.correlation import request_context
from enterprise_logging.core.logger import LogDispatcher, Logger
from enterprise_logging.core.types import LogLevel, LogRecord
from enterprise_logging.transport.factory import TransportRegistry


class MemoryTransport:
    name = "memory"

    def __init__(self) -> None:
        self.events: list[str] = []

    def emit(self, payload: str, record: LogRecord) -> None:
        del record
        self.events.append(payload)

    def flush(self) -> None:
        pass

    def close(self) -> None:
        pass


def _memory_logger(async_enabled: bool = False) -> tuple[Logger, MemoryTransport, LogDispatcher]:
    memory = MemoryTransport()
    registry = TransportRegistry()
    registry.register("memory", lambda _config: memory)
    config = LoggerConfig(
        level=LogLevel.INFO,
        outputs=(OutputConfig(type="memory"),),
        async_=AsyncConfig(enabled=async_enabled, batch_size=2, flush_interval_seconds=0.01),
    )
    dispatcher = LogDispatcher(config=config, registry=registry)
    return Logger(config=config, dispatcher=dispatcher, module="unit"), memory, dispatcher


def test_logger_masks_and_sanitizes() -> None:
    logger, memory, dispatcher = _memory_logger()

    logger.info("hello\nworld", {"password": "clear"})
    dispatcher.flush()

    event = json.loads(memory.events[0])
    assert event["message"] == "hello\\nworld"
    assert event["metadata"]["password"] == "***MASKED***"


def test_lazy_message_not_evaluated_when_disabled() -> None:
    called = False
    logger, _memory, dispatcher = _memory_logger()

    def expensive() -> str:
        nonlocal called
        called = True
        return "expensive"

    logger.debug(expensive)
    dispatcher.flush()

    assert called is False


def test_async_context_correlation_is_emitted() -> None:
    logger, memory, dispatcher = _memory_logger(async_enabled=True)

    with request_context(correlation_id="corr-1", tenant="tenant-a"):
        logger.info("inside")
    dispatcher.flush()
    dispatcher.close()

    event = json.loads(memory.events[0])
    assert event["correlationId"] == "corr-1"
    assert event["context"]["tenant"] == "tenant-a"


def test_concurrent_context_isolation() -> None:
    logger, memory, dispatcher = _memory_logger()

    def worker(correlation_id: str) -> None:
        with request_context(correlation_id=correlation_id):
            logger.info("request")

    threads = [threading.Thread(target=worker, args=(f"corr-{index}",)) for index in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    dispatcher.flush()

    emitted = {json.loads(event)["correlationId"] for event in memory.events}
    assert emitted == {f"corr-{index}" for index in range(10)}


def test_error_serialization_includes_stack_and_cause() -> None:
    logger, memory, dispatcher = _memory_logger()

    try:
        try:
            raise ValueError("inner")
        except ValueError as exc:
            raise RuntimeError("outer") from exc
    except RuntimeError as exc:
        logger.error("failed", exc, {"token": "secret"})

    dispatcher.flush()
    event = json.loads(memory.events[0])
    assert event["error"]["type"] == "RuntimeError"
    assert event["error"]["cause"]["type"] == "ValueError"
    assert event["metadata"]["token"] == "***MASKED***"
