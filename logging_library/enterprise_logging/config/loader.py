from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from enterprise_logging.config.schema import LoggerConfig, config_from_mapping
from enterprise_logging.core.exceptions import LoggingConfigurationError


def load_config(
    source: str | Path | dict[str, Any] | LoggerConfig | None = None,
    *,
    env_prefix: str = "LOGGING_",
    overrides: dict[str, Any] | None = None,
) -> LoggerConfig:
    if isinstance(source, LoggerConfig):
        base = _config_to_mapping(source)
    elif isinstance(source, dict) or source is None:
        base = dict(source or {})
    else:
        base = _read_config_file(Path(source))

    merged = _deep_merge(base, _env_mapping(env_prefix))
    merged = _deep_merge(merged, overrides or {})
    return config_from_mapping(merged)


def _read_config_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise LoggingConfigurationError(f"Config file does not exist: {path}")
    text = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix == ".json":
        value = json.loads(text)
    elif suffix in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError as exc:
            raise LoggingConfigurationError(
                "Install enterprise-logging-library[yaml] for YAML config"
            ) from exc
        value = yaml.safe_load(text) or {}
    else:
        raise LoggingConfigurationError("Config files must be .json, .yaml, or .yml")
    if not isinstance(value, dict):
        raise LoggingConfigurationError("Config root must be an object")
    return value


def _env_mapping(prefix: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    mapping = {
        "ENABLED": ("enabled",),
        "LEVEL": ("level",),
        "FORMAT": ("format",),
        "APPLICATION": ("metadata", "application"),
        "ENVIRONMENT": ("metadata", "environment"),
        "SERVICE": ("metadata", "service"),
        "VERSION": ("metadata", "version"),
        "ASYNC_ENABLED": ("async", "enabled"),
        "ASYNC_QUEUE_SIZE": ("async", "queue_size"),
        "ASYNC_BATCH_SIZE": ("async", "batch_size"),
        "MASKING_ENABLED": ("masking", "enabled"),
        "MASK_VALUE": ("masking", "mask"),
        "SANITIZE_NEWLINES": ("sanitize_newlines",),
    }
    for env_name, path in mapping.items():
        key = f"{prefix}{env_name}"
        if key in os.environ:
            _set_nested(result, path, os.environ[key])
    return result


def _set_nested(target: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    current = target
    for part in path[:-1]:
        next_value = current.setdefault(part, {})
        if not isinstance(next_value, dict):
            next_value = {}
            current[part] = next_value
        current = next_value
    current[path[-1]] = value


def _deep_merge(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    merged = dict(left)
    for key, value in right.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _config_to_mapping(config: LoggerConfig) -> dict[str, Any]:
    return {
        "enabled": config.enabled,
        "level": config.level.name,
        "format": config.format,
        "timestamp_format": config.timestamp_format,
        "outputs": list(config.outputs),
        "metadata": config.metadata.__dict__,
        "masking": config.masking.__dict__,
        "async": config.async_.__dict__,
        "sanitize_newlines": config.sanitize_newlines,
        "max_payload_depth": config.max_payload_depth,
        "max_payload_items": config.max_payload_items,
    }
