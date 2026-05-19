"""Tests for SQL builder."""

import pytest

from app_error_db_log.config import AppErrorLogConfig
from app_error_db_log.models import ErrorLogEntry
from app_error_db_log.sql_builder import (
    build_insert_sql,
    build_stored_procedure_sql,
    entry_to_parameters,
    validate_identifier,
)


def test_build_insert_sql_defaults() -> None:
    config = AppErrorLogConfig.from_dict({"connection_string": "Driver=test"})

    sql = build_insert_sql(config)

    assert "INSERT INTO [GenAI_V1].[ErrorLog]" in sql
    assert sql.count("?") == 14


def test_build_stored_procedure_sql() -> None:
    config = AppErrorLogConfig.from_dict(
        {
            "connection_string": "Driver=test",
            "stored_procedure_name": "GenAI_V1.InsertErrorLog",
        }
    )

    sql = build_stored_procedure_sql(config)

    assert sql.startswith("EXEC [GenAI_V1].[InsertErrorLog]")
    assert sql.count("?") == 14


def test_validate_identifier_rejects_unsafe_value() -> None:
    with pytest.raises(ValueError):
        validate_identifier("Bad;DROP TABLE X")


def test_entry_to_parameters_count() -> None:
    params = entry_to_parameters(ErrorLogEntry(error_message="x"))

    assert len(params) == 14

