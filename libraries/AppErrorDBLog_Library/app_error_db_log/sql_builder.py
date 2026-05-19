"""Safe SQL statement builders."""

from __future__ import annotations

import re

from app_error_db_log.config import AppErrorLogConfig
from app_error_db_log.models import ErrorLogEntry

SAFE_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
ENTRY_FIELDS = (
    "correlation_id",
    "session_id",
    "user_id",
    "application_name",
    "module_name",
    "error_type",
    "error_code",
    "error_message",
    "stack_trace",
    "request_path",
    "request_payload",
    "additional_info_json",
    "ip_address",
    "created_date",
)


def validate_identifier(identifier: str) -> str:
    """Validate and quote a SQL Server identifier."""

    if not SAFE_IDENTIFIER_PATTERN.fullmatch(identifier):
        raise ValueError(f"Unsafe SQL identifier: {identifier}")
    return f"[{identifier}]"


def build_insert_sql(config: AppErrorLogConfig) -> str:
    """Build a parameterized INSERT statement."""

    schema = validate_identifier(config.schema_name)
    table = validate_identifier(config.table_name)
    columns = [validate_identifier(config.columns[field]) for field in ENTRY_FIELDS]
    placeholders = ", ".join("?" for _ in ENTRY_FIELDS)
    return (
        f"INSERT INTO {schema}.{table} ({', '.join(columns)}) "
        f"VALUES ({placeholders})"
    )


def build_stored_procedure_sql(config: AppErrorLogConfig) -> str:
    """Build parameterized stored procedure execution SQL."""

    if not config.stored_procedure_name:
        raise ValueError("Stored procedure name is not configured.")
    parts = config.stored_procedure_name.split(".")
    if len(parts) == 2:
        procedure_name = ".".join(validate_identifier(part) for part in parts)
    elif len(parts) == 1:
        procedure_name = validate_identifier(parts[0])
    else:
        raise ValueError("Stored procedure name must be one or two identifiers.")
    placeholders = ", ".join("?" for _ in ENTRY_FIELDS)
    return f"EXEC {procedure_name} {placeholders}"


def entry_to_parameters(entry: ErrorLogEntry) -> tuple[object, ...]:
    """Convert an entry to SQL parameters in column order."""

    return tuple(getattr(entry, field) for field in ENTRY_FIELDS)

