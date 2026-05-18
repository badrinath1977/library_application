from __future__ import annotations

from enterprise_logging import get_logger, initialize_logger, register_transport, shutdown
from enterprise_logging.config.schema import OutputConfig
from enterprise_logging.core.types import LogRecord


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
        self.flush()


memory_transport = MemoryTransport()


def create_memory_transport(config: OutputConfig) -> MemoryTransport:
    del config
    return memory_transport


register_transport("memory", create_memory_transport)
initialize_logger(
    {
        "level": "DEBUG",
        "format": "json",
        "outputs": [{"type": "memory", "enabled": True}],
        "async": {"enabled": False},
    }
)

get_logger("plugin.example").info("custom.transport.ready")
shutdown()
