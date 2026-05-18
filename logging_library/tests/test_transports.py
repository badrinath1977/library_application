import json

import pytest

from enterprise_logging import flush, get_logger, initialize_logger, register_transport, shutdown
from enterprise_logging.config.schema import OutputConfig
from enterprise_logging.core.exceptions import LoggingConfigurationError
from enterprise_logging.core.types import LogRecord


class MemoryTransport:
    name = "memory-test"

    def __init__(self) -> None:
        self.events: list[str] = []

    def emit(self, payload: str, record: LogRecord) -> None:
        del record
        self.events.append(payload)

    def flush(self) -> None:
        pass

    def close(self) -> None:
        pass


def test_registered_custom_transport() -> None:
    memory = MemoryTransport()

    def factory(config: OutputConfig) -> MemoryTransport:
        del config
        return memory

    register_transport("memory-test", factory)
    initialize_logger(
        {
            "level": "INFO",
            "outputs": [{"type": "memory-test"}],
            "async": {"enabled": False},
        }
    )
    get_logger("transport").info("hello")
    flush()
    shutdown()

    assert json.loads(memory.events[0])["message"] == "hello"


def test_rolling_file_transport_writes_json(tmp_path) -> None:
    log_path = tmp_path / "app.log"
    initialize_logger(
        {
            "level": "INFO",
            "outputs": [{"type": "file", "path": str(log_path), "format": "json"}],
            "async": {"enabled": False},
        }
    )
    get_logger("file").info("file.event")
    shutdown()

    assert "file.event" in log_path.read_text(encoding="utf-8")


def test_provider_transport_requires_endpoint() -> None:
    with pytest.raises(LoggingConfigurationError):
        initialize_logger(
            {
                "outputs": [{"type": "opentelemetry", "options": {}}],
                "async": {"enabled": False},
            }
        )
