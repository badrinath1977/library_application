from __future__ import annotations

import os
import socket
import threading
from collections.abc import Callable
from typing import Any

from enterprise_logging.config.schema import LoggerConfig
from enterprise_logging.context.correlation import (
    bind_context,
    get_context,
    get_correlation_id,
    get_request_id,
)
from enterprise_logging.core.contracts import Formatter, Transport
from enterprise_logging.core.types import ErrorInfo, LogLevel, LogRecord
from enterprise_logging.formatter.factory import create_formatter
from enterprise_logging.masking.masker import SensitiveDataMasker
from enterprise_logging.serializers.safe import SafeSerializer
from enterprise_logging.transport.async_transport import AsyncDispatcher
from enterprise_logging.transport.factory import TransportRegistry

Message = str | Callable[[], str]


class Logger:
    def __init__(
        self,
        *,
        config: LoggerConfig,
        dispatcher: LogDispatcher,
        module: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> None:
        self._config = config
        self._dispatcher = dispatcher
        self._module = module
        self._context = dict(context or {})
        self._serializer = SafeSerializer(
            max_depth=config.max_payload_depth,
            max_items=config.max_payload_items,
        )
        self._masker = SensitiveDataMasker(config.masking)

    def trace(self, message: Message, data: Any = None) -> None:
        self._log(LogLevel.TRACE, message, data=data)

    def debug(self, message: Message, data: Any = None) -> None:
        self._log(LogLevel.DEBUG, message, data=data)

    def info(self, message: Message, data: Any = None) -> None:
        self._log(LogLevel.INFO, message, data=data)

    def warn(self, message: Message, data: Any = None) -> None:
        self._log(LogLevel.WARN, message, data=data)

    def error(self, message: Message, error_or_data: Any = None, data: Any = None) -> None:
        self._log(LogLevel.ERROR, message, error_or_data=error_or_data, data=data)

    def fatal(self, message: Message, error_or_data: Any = None, data: Any = None) -> None:
        self._log(LogLevel.FATAL, message, error_or_data=error_or_data, data=data)

    def child(self, context: dict[str, Any] | None = None, **values: Any) -> Logger:
        merged = dict(self._context)
        if context:
            merged.update(context)
        merged.update(values)
        return Logger(
            config=self._config,
            dispatcher=self._dispatcher,
            module=self._module,
            context=merged,
        )

    def bind(self, **values: Any) -> None:
        bind_context(**values)

    def _log(
        self,
        level: LogLevel,
        message: Message,
        *,
        error_or_data: Any = None,
        data: Any = None,
    ) -> None:
        if not self._config.enabled or level < self._config.level:
            return
        text = message() if callable(message) else str(message)
        if self._config.sanitize_newlines:
            text = text.replace("\r", "\\r").replace("\n", "\\n")

        error_info: ErrorInfo | None = None
        metadata_input: Any = data
        if isinstance(error_or_data, BaseException):
            error_info = self._serializer.error(error_or_data)
        elif error_or_data is not None:
            metadata_input = (
                error_or_data
                if data is None
                else {"errorData": error_or_data, "data": data}
            )

        metadata = (
            self._masker.mask(self._serializer.serialize(metadata_input))
            if metadata_input is not None
            else {}
        )
        if not isinstance(metadata, dict):
            metadata = {"value": metadata}
        metadata = {**self._config.metadata.custom, **metadata}
        context = {**get_context(), **self._context}
        record = LogRecord.create(
            level=level,
            message=text,
            module=self._module,
            application=self._config.metadata.application,
            environment=self._config.metadata.environment,
            service=self._config.metadata.service,
            hostname=socket.gethostname() if self._config.metadata.include_hostname else "",
            process_id=os.getpid() if self._config.metadata.include_process_id else 0,
            thread_id=threading.get_ident() if self._config.metadata.include_thread_id else 0,
            correlation_id=get_correlation_id(),
            request_id=get_request_id(),
            version=self._config.metadata.version,
            metadata=metadata,
            context=self._masker.mask(self._serializer.serialize(context)),
            error=error_info,
        )
        self._dispatcher.emit(record)


class LogDispatcher:
    def __init__(
        self,
        *,
        config: LoggerConfig,
        registry: TransportRegistry | None = None,
    ) -> None:
        registry = registry or TransportRegistry()
        self._config = config
        self._transports: tuple[tuple[Transport, Formatter], ...] = tuple(
            (
                registry.create(output),
                create_formatter(
                    output.format or config.format,
                    timestamp_format=config.timestamp_format,
                ),
            )
            for output in config.outputs
            if output.enabled
        )
        self._async = (
            AsyncDispatcher(transports=self._transports, config=config.async_)
            if config.async_.enabled
            else None
        )

    def emit(self, record: LogRecord) -> None:
        if self._async:
            self._async.emit(record)
            return
        for transport, formatter in self._transports:
            transport.emit(formatter.format(record), record)

    def flush(self) -> None:
        if self._async:
            self._async.flush()
            return
        for transport, _formatter in self._transports:
            transport.flush()

    def close(self) -> None:
        if self._async:
            self._async.close()
            return
        for transport, _formatter in self._transports:
            transport.close()
