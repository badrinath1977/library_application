"""Configuration loading for app_error_db_log."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

DEFAULT_SCHEMA = "GenAI_V1"
DEFAULT_TABLE = "ErrorLog"
DEFAULT_SECTION = "AppErrorDBLog"

DEFAULT_COLUMNS: dict[str, str] = {
    "correlation_id": "CorrelationId",
    "session_id": "SessionId",
    "user_id": "UserId",
    "application_name": "ApplicationName",
    "module_name": "ModuleName",
    "error_type": "ErrorType",
    "error_code": "ErrorCode",
    "error_message": "ErrorMessage",
    "stack_trace": "StackTrace",
    "request_path": "RequestPath",
    "request_payload": "RequestPayload",
    "additional_info_json": "AdditionalInfoJson",
    "ip_address": "IPAddress",
    "created_date": "CreatedDate",
}


@dataclass(frozen=True, slots=True)
class AppErrorLogConfig:
    """Configuration for SQL Server error logging."""

    connection_string: str
    schema_name: str = DEFAULT_SCHEMA
    table_name: str = DEFAULT_TABLE
    stored_procedure_name: str | None = None
    application_name: str = "PythonApplication"
    timeout_seconds: int = 30
    retry_count: int = 2
    fallback_file_path: str = "logs/app_error_db_fallback.log"
    suppress_logger_errors: bool = True
    suppress_original_exception: bool = False
    columns: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_COLUMNS))

    @classmethod
    def from_file(
        cls,
        config_path: str | Path,
        section: str = DEFAULT_SECTION,
    ) -> AppErrorLogConfig:
        """Load config from JSON or simple YAML file."""

        path = Path(config_path)
        if not path.is_file():
            raise FileNotFoundError(f"Config file not found: {path}")
        data = _load_config_file(path)
        section_data = data.get(section, data)
        if not isinstance(section_data, dict):
            raise ValueError(f"Config section '{section}' must be an object.")
        return cls.from_dict(section_data)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> AppErrorLogConfig:
        """Create config from a dictionary."""

        connection_string = str(
            data.get("connection_string") or os.getenv("APP_ERROR_DB_CONNECTION", "")
        )
        columns = dict(DEFAULT_COLUMNS)
        provided_columns = data.get("columns", {})
        if isinstance(provided_columns, dict):
            columns.update(
                {str(key): str(value) for key, value in provided_columns.items()}
            )
        return cls(
            connection_string=connection_string,
            schema_name=str(data.get("schema_name") or DEFAULT_SCHEMA),
            table_name=str(data.get("table_name") or DEFAULT_TABLE),
            stored_procedure_name=(
                str(data["stored_procedure_name"])
                if data.get("stored_procedure_name")
                else None
            ),
            application_name=str(data.get("application_name") or "PythonApplication"),
            timeout_seconds=int(data.get("timeout_seconds") or 30),
            retry_count=int(data.get("retry_count") or 2),
            fallback_file_path=str(
                data.get("fallback_file_path") or "logs/app_error_db_fallback.log"
            ),
            suppress_logger_errors=bool(data.get("suppress_logger_errors", True)),
            suppress_original_exception=bool(
                data.get("suppress_original_exception", False)
            ),
            columns=columns,
        )

    @classmethod
    def from_env(cls, prefix: str = "APP_ERROR_DB_") -> AppErrorLogConfig:
        """Create config from environment variables."""

        return cls(
            connection_string=os.getenv(f"{prefix}CONNECTION_STRING", ""),
            schema_name=os.getenv(f"{prefix}SCHEMA_NAME", DEFAULT_SCHEMA),
            table_name=os.getenv(f"{prefix}TABLE_NAME", DEFAULT_TABLE),
            stored_procedure_name=os.getenv(f"{prefix}STORED_PROCEDURE_NAME") or None,
            application_name=os.getenv(
                f"{prefix}APPLICATION_NAME",
                "PythonApplication",
            ),
            timeout_seconds=int(os.getenv(f"{prefix}TIMEOUT_SECONDS", "30")),
            retry_count=int(os.getenv(f"{prefix}RETRY_COUNT", "2")),
            fallback_file_path=os.getenv(
                f"{prefix}FALLBACK_FILE_PATH",
                "logs/app_error_db_fallback.log",
            ),
            suppress_logger_errors=_env_bool(
                os.getenv(f"{prefix}SUPPRESS_LOGGER_ERRORS"),
                default=True,
            ),
            suppress_original_exception=_env_bool(
                os.getenv(f"{prefix}SUPPRESS_ORIGINAL_EXCEPTION"),
                default=False,
            ),
        )


def _load_config_file(path: Path) -> dict[str, Any]:
    suffix = path.suffix.lower()
    content = path.read_text(encoding="utf-8")
    if suffix == ".json":
        loaded = json.loads(content)
    elif suffix in {".yaml", ".yml"}:
        loaded = _parse_simple_yaml(content)
    else:
        raise ValueError("Only JSON and YAML config files are supported.")
    if not isinstance(loaded, dict):
        raise ValueError("Config root must be an object.")
    return loaded


def _parse_simple_yaml(content: str) -> dict[str, Any]:
    """Parse simple YAML via PyYAML when present, with minimal fallback."""

    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        return _parse_flat_yaml(content)
    loaded = yaml.safe_load(content) or {}
    if not isinstance(loaded, dict):
        raise ValueError("YAML config root must be an object.")
    return loaded


def _parse_flat_yaml(content: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    current_section: dict[str, Any] | None = None
    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if not line.startswith(" ") and line.endswith(":"):
            section_name = line[:-1].strip()
            current_section = {}
            result[section_name] = current_section
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        target = (
            current_section
            if line.startswith(" ") and current_section is not None
            else result
        )
        target[key.strip()] = _coerce_yaml_scalar(value.strip())
    return result


def _coerce_yaml_scalar(value: str) -> object:
    if value in {"null", "None", "~"}:
        return None
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    return value


def _env_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y"}
