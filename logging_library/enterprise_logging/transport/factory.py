from __future__ import annotations

from collections.abc import Callable

from enterprise_logging.config.schema import OutputConfig
from enterprise_logging.core.contracts import Transport
from enterprise_logging.core.exceptions import LoggingConfigurationError
from enterprise_logging.transport.console import ConsoleTransport
from enterprise_logging.transport.file import RollingFileTransport
from enterprise_logging.transport.plugins import ProviderHttpTransport

TransportFactory = Callable[[OutputConfig], Transport]


class TransportRegistry:
    def __init__(self) -> None:
        self._factories: dict[str, TransportFactory] = {
            "console": lambda _config: ConsoleTransport(),
            "file": self._file_transport,
            "elk": lambda config: ProviderHttpTransport("elk", config.options),
            "splunk": lambda config: ProviderHttpTransport("splunk", config.options),
            "datadog": lambda config: ProviderHttpTransport("datadog", config.options),
            "cloudwatch": lambda config: ProviderHttpTransport("cloudwatch", config.options),
            "opentelemetry": lambda config: ProviderHttpTransport(
                "opentelemetry",
                config.options,
            ),
            "kafka": lambda config: ProviderHttpTransport("kafka", config.options),
        }

    def register(self, name: str, factory: TransportFactory) -> None:
        self._factories[name] = factory

    def create(self, config: OutputConfig) -> Transport:
        try:
            return self._factories[config.type](config)
        except KeyError as exc:
            raise LoggingConfigurationError(f"No transport registered for {config.type}") from exc

    @staticmethod
    def _file_transport(config: OutputConfig) -> Transport:
        if not config.path:
            raise LoggingConfigurationError("file transport requires a path")
        return RollingFileTransport(config.path, config.rolling_policy)
