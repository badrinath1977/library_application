"""Tests for configuration loading."""

from __future__ import annotations

import json
from pathlib import Path

from app_error_db_log.config import AppErrorLogConfig


def test_config_from_dict_defaults() -> None:
    config = AppErrorLogConfig.from_dict({"connection_string": "Driver=test"})

    assert config.schema_name == "GenAI_V1"
    assert config.table_name == "ErrorLog"
    assert config.columns["error_message"] == "ErrorMessage"


def test_config_from_json_file(tmp_path: Path) -> None:
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps({"AppErrorDBLog": {"connection_string": "Driver=test"}}),
        encoding="utf-8",
    )

    config = AppErrorLogConfig.from_file(config_path)

    assert config.connection_string == "Driver=test"


def test_config_from_env(monkeypatch) -> None:
    monkeypatch.setenv("APP_ERROR_DB_CONNECTION_STRING", "Driver=env")

    config = AppErrorLogConfig.from_env()

    assert config.connection_string == "Driver=env"

