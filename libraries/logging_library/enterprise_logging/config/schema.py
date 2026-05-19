from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any, Literal

from libraries.logging_library.enterprise_logging.core.exceptions import LoggingConfigurationError
from libraries.logging_library.enterprise_logging.core.types import LogLevel

LogFormat = Literal["json", "text", "pretty"]
OutputType = str


@dataclass(frozen=True, slots=True)
class RollingPolicy:
    max_bytes: int = 10 * 1024 * 1024
    backup_count: int = 5
    compression: bool = False


@dataclass(frozen=True, slots=True)
class OutputConfig:
    type: OutputType
    enabled: bool = True
    format: LogFormat | None = None
    path: str | None = None
    rolling_policy: RollingPolicy = field(default_factory=RollingPolicy)
    options: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class MaskingConfig:
    enabled: bool = True
    mask: str = "***MASKED***"
    sensitive_keys: tuple[str, ...] = (
        "password",
        "token",
        "accessToken",
        "refreshToken",
        "apiKey",
        "authorization",
        "secret",
        "cookie",
        "cookies",
        "session",
        "sessionId",
        "set-cookie",
    )
    sensitive_patterns: tuple[str, ...] = (
        r"(?i)(bearer\s+)[A-Za-z0-9._\-+/=]+",
        r"(?i)(basic\s+)[A-Za-z0-9._\-+/=]+",
    )


@dataclass(frozen=True, slots=True)
class MetadataConfig:
    application: str = "application"
    environment: str = "development"
    service: str = "service"
    version: str | None = None
    include_hostname: bool = True
    include_process_id: bool = True
    include_thread_id: bool = True
    custom: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AsyncConfig:
    enabled: bool = True
    queue_size: int = 10000
    batch_size: int = 100
    flush_interval_seconds: float = 1.0
    drop_when_full: bool = False
    fail_fast: bool = False


@dataclass(frozen=True, slots=True)
class LoggerConfig:
    enabled: bool = True
    level: LogLevel = LogLevel.INFO
    format: LogFormat = "json"
    timestamp_format: str = "iso8601"
    outputs: tuple[OutputConfig, ...] = field(
        default_factory=lambda: (OutputConfig(type="console"),)
    )
    metadata: MetadataConfig = field(default_factory=MetadataConfig)
    masking: MaskingConfig = field(default_factory=MaskingConfig)
    async_: AsyncConfig = field(default_factory=AsyncConfig)
    sanitize_newlines: bool = True
    max_payload_depth: int = 20
    max_payload_items: int = 1000

    def with_overrides(self, **overrides: Any) -> LoggerConfig:
        return replace(self, **overrides)


def _as_bool(value: Any, field_name: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes", "y", "on"}:
            return True
        if normalized in {"false", "0", "no", "n", "off"}:
            return False
    raise LoggingConfigurationError(f"{field_name} must be a boolean")


def _as_int(value: Any, field_name: str, minimum: int = 0) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise LoggingConfigurationError(f"{field_name} must be an integer") from exc
    if parsed < minimum:
        raise LoggingConfigurationError(f"{field_name} must be >= {minimum}")
    return parsed


def _as_float(value: Any, field_name: str, minimum: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise LoggingConfigurationError(f"{field_name} must be a number") from exc
    if parsed < minimum:
        raise LoggingConfigurationError(f"{field_name} must be >= {minimum}")
    return parsed


def config_from_mapping(raw: dict[str, Any] | None) -> LoggerConfig:
    data = dict(raw or {})
    defaults = LoggerConfig()
    level = LogLevel.parse(data.get("level", defaults.level))
    fmt = data.get("format", defaults.format)
    if fmt not in {"json", "text", "pretty"}:
        raise LoggingConfigurationError("format must be one of: json, text, pretty")

    metadata_data = dict(data.get("metadata", {}))
    metadata = MetadataConfig(
        application=str(metadata_data.get("application", defaults.metadata.application)),
        environment=str(metadata_data.get("environment", defaults.metadata.environment)),
        service=str(metadata_data.get("service", defaults.metadata.service)),
        version=metadata_data.get("version", defaults.metadata.version),
        include_hostname=_as_bool(
            metadata_data.get("include_hostname", defaults.metadata.include_hostname),
            "metadata.include_hostname",
        ),
        include_process_id=_as_bool(
            metadata_data.get("include_process_id", defaults.metadata.include_process_id),
            "metadata.include_process_id",
        ),
        include_thread_id=_as_bool(
            metadata_data.get("include_thread_id", defaults.metadata.include_thread_id),
            "metadata.include_thread_id",
        ),
        custom=dict(metadata_data.get("custom", defaults.metadata.custom)),
    )

    masking_data = dict(data.get("masking", {}))
    masking = MaskingConfig(
        enabled=_as_bool(masking_data.get("enabled", defaults.masking.enabled), "masking.enabled"),
        mask=str(masking_data.get("mask", defaults.masking.mask)),
        sensitive_keys=tuple(masking_data.get("sensitive_keys", defaults.masking.sensitive_keys)),
        sensitive_patterns=tuple(
            masking_data.get("sensitive_patterns", defaults.masking.sensitive_patterns)
        ),
    )

    async_data = dict(data.get("async", data.get("async_", {})))
    async_config = AsyncConfig(
        enabled=_as_bool(async_data.get("enabled", defaults.async_.enabled), "async.enabled"),
        queue_size=_as_int(
            async_data.get("queue_size", defaults.async_.queue_size),
            "async.queue_size",
            1,
        ),
        batch_size=_as_int(
            async_data.get("batch_size", defaults.async_.batch_size),
            "async.batch_size",
            1,
        ),
        flush_interval_seconds=_as_float(
            async_data.get("flush_interval_seconds", defaults.async_.flush_interval_seconds),
            "async.flush_interval_seconds",
            0.001,
        ),
        drop_when_full=_as_bool(
            async_data.get("drop_when_full", defaults.async_.drop_when_full),
            "async.drop_when_full",
        ),
        fail_fast=_as_bool(
            async_data.get("fail_fast", defaults.async_.fail_fast),
            "async.fail_fast",
        ),
    )

    configured_outputs = data.get("outputs", defaults.outputs)
    outputs = tuple(_parse_output(item, index) for index, item in enumerate(configured_outputs))
    if not outputs:
        raise LoggingConfigurationError("At least one output is required")

    return LoggerConfig(
        enabled=_as_bool(data.get("enabled", defaults.enabled), "enabled"),
        level=level,
        format=fmt,
        timestamp_format=str(data.get("timestamp_format", defaults.timestamp_format)),
        outputs=outputs,
        metadata=metadata,
        masking=masking,
        async_=async_config,
        sanitize_newlines=_as_bool(
            data.get("sanitize_newlines", defaults.sanitize_newlines),
            "sanitize_newlines",
        ),
        max_payload_depth=_as_int(
            data.get("max_payload_depth", defaults.max_payload_depth),
            "max_payload_depth",
            1,
        ),
        max_payload_items=_as_int(
            data.get("max_payload_items", defaults.max_payload_items),
            "max_payload_items",
            1,
        ),
    )


def _parse_output(item: Any, index: int) -> OutputConfig:
    if isinstance(item, OutputConfig):
        return item
    if not isinstance(item, dict):
        raise LoggingConfigurationError(f"outputs[{index}] must be an object")
    output_type = item.get("type")
    if not isinstance(output_type, str) or not output_type.strip():
        raise LoggingConfigurationError(f"outputs[{index}].type must be a non-empty string")
    output_format = item.get("format")
    if output_format is not None and output_format not in {"json", "text", "pretty"}:
        raise LoggingConfigurationError(f"outputs[{index}].format is invalid")
    rolling_data = dict(item.get("rolling_policy", {}))
    rolling = RollingPolicy(
        max_bytes=_as_int(
            rolling_data.get("max_bytes", RollingPolicy().max_bytes),
            "rolling.max_bytes",
            1,
        ),
        backup_count=_as_int(
            rolling_data.get("backup_count", RollingPolicy().backup_count),
            "rolling.backup_count",
            0,
        ),
        compression=_as_bool(
            rolling_data.get("compression", RollingPolicy().compression),
            "rolling.compression",
        ),
    )
    path = item.get("path")
    if output_type == "file" and not path:
        raise LoggingConfigurationError("file outputs require path")
    if path:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
    return OutputConfig(
        type=output_type,
        enabled=_as_bool(item.get("enabled", True), f"outputs[{index}].enabled"),
        format=output_format,
        path=path,
        rolling_policy=rolling,
        options=dict(item.get("options", {})),
    )
