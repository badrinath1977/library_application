from __future__ import annotations

from typing import Any

from enterprise_logging.config.loader import load_config
from enterprise_logging.config.schema import LoggerConfig
from enterprise_logging.context.correlation import with_correlation_id
from enterprise_logging.core.logger import LogDispatcher, Logger
from enterprise_logging.core.types import LogLevel
from enterprise_logging.transport.factory import TransportRegistry

_config: LoggerConfig = load_config()
_registry = TransportRegistry()
_dispatcher = LogDispatcher(config=_config, registry=_registry)


def initialize_logger(
    config: str | dict[str, Any] | LoggerConfig | None = None,
    *,
    overrides: dict[str, Any] | None = None,
) -> Logger:
    global _config, _dispatcher
    _dispatcher.close()
    _config = load_config(config, overrides=overrides)
    _dispatcher = LogDispatcher(config=_config, registry=_registry)
    return get_logger()


def get_logger(module_name: str | None = None) -> Logger:
    return Logger(config=_config, dispatcher=_dispatcher, module=module_name)


def set_log_level(level: str | int | LogLevel) -> None:
    global _config
    _config = _config.with_overrides(level=LogLevel.parse(level))


def register_transport(name: str, factory: Any) -> None:
    _registry.register(name, factory)


def flush() -> None:
    _dispatcher.flush()


def shutdown() -> None:
    _dispatcher.close()


__all__ = [
    "flush",
    "get_logger",
    "initialize_logger",
    "register_transport",
    "set_log_level",
    "shutdown",
    "with_correlation_id",
]
