"""Tests for KeyVaultManager."""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

import libraries.Keyvault_library.keyvault_library.manager as manager_module
from libraries.Keyvault_library.keyvault_library import KeyVaultManager
from libraries.Keyvault_library.keyvault_library.exceptions import (
    ConfigFileNotFoundError,
    InvalidConfigJsonError,
    InvalidConfigValueError,
    KeyVaultLibraryError,
    LoggerSetupError,
    MissingConfigKeyError,
)
from libraries.Keyvault_library.keyvault_library.logger import get_log_file_name


@pytest.fixture
def valid_config_data(tmp_path: Path) -> dict[str, object]:
    return {
        "KeyVaultURL": "https://testingkeyvalut.vault.azure.net/",
        "SecretsName": ["sec1", "sec2", "sec3"],
        "Key": ["k1", "k2"],
        "LogLocation": str(tmp_path / "logs"),
    }


@pytest.fixture
def config_file(tmp_path: Path, valid_config_data: dict[str, object]) -> Path:
    path = tmp_path / "config.json"
    write_config(path, valid_config_data)
    return path


def write_config(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_valid_config_loads_successfully(config_file: Path) -> None:
    manager = KeyVaultManager(config_file)

    assert manager.get_keyvault_url() == "https://testingkeyvalut.vault.azure.net/"


def test_from_file_loads_explicit_application_config(config_file: Path) -> None:
    manager = KeyVaultManager.from_file(config_file)

    assert manager.config_path == config_file
    assert manager.get_keyvault_url() == "https://testingkeyvalut.vault.azure.net/"


def test_from_dict_loads_application_owned_config(
    valid_config_data: dict[str, object],
) -> None:
    manager = KeyVaultManager.from_dict(valid_config_data)

    assert manager.config_path is None
    assert manager.get_secret_names() == ("sec1", "sec2", "sec3")
    assert manager.get_keys() == ("k1", "k2")


def test_from_env_loads_config_path_from_environment(
    config_file: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("KEYVAULT_LIBRARY_CONFIG", str(config_file))

    manager = KeyVaultManager.from_env()

    assert manager.config_path == config_file


def test_from_env_raises_for_missing_environment_variable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("KEYVAULT_LIBRARY_CONFIG", raising=False)

    with pytest.raises(MissingConfigKeyError):
        KeyVaultManager.from_env()


def test_from_env_raises_for_empty_environment_variable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("KEYVAULT_LIBRARY_CONFIG", "   ")

    with pytest.raises(InvalidConfigValueError):
        KeyVaultManager.from_env()


def test_reload_config_raises_when_manager_is_created_from_dict(
    valid_config_data: dict[str, object],
) -> None:
    manager = KeyVaultManager.from_dict(valid_config_data)

    with pytest.raises(KeyVaultLibraryError):
        manager.reload_config()


def test_missing_config_file_raises_config_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(ConfigFileNotFoundError):
        KeyVaultManager(tmp_path / "missing.json")


def test_invalid_json_raises_invalid_config_json(tmp_path: Path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text("{ invalid json", encoding="utf-8")

    with pytest.raises(InvalidConfigJsonError):
        KeyVaultManager(config_file)


@pytest.mark.parametrize(
    "missing_key",
    ["KeyVaultURL", "SecretsName", "Key", "LogLocation"],
)
def test_missing_keys_raise_missing_config_key_error(
    tmp_path: Path,
    valid_config_data: dict[str, object],
    missing_key: str,
) -> None:
    valid_config_data.pop(missing_key)
    config_file = tmp_path / "config.json"
    write_config(config_file, valid_config_data)

    with pytest.raises(MissingConfigKeyError):
        KeyVaultManager(config_file)


@pytest.mark.parametrize(
    ("key_name", "value"),
    [
        ("KeyVaultURL", ""),
        ("SecretsName", []),
        ("Key", []),
        ("LogLocation", ""),
        ("SecretsName", "sec1"),
        ("Key", "k1"),
    ],
)
def test_invalid_values_raise_invalid_config_value_error(
    tmp_path: Path,
    valid_config_data: dict[str, object],
    key_name: str,
    value: object,
) -> None:
    valid_config_data[key_name] = value
    config_file = tmp_path / "config.json"
    write_config(config_file, valid_config_data)

    with pytest.raises(InvalidConfigValueError):
        KeyVaultManager(config_file)


def test_get_keyvault_url_returns_configured_value(config_file: Path) -> None:
    manager = KeyVaultManager(config_file)

    assert manager.get_keyvault_url() == "https://testingkeyvalut.vault.azure.net/"


def test_get_secret_names_returns_tuple(config_file: Path) -> None:
    manager = KeyVaultManager(config_file)

    assert manager.get_secret_names() == ("sec1", "sec2", "sec3")


def test_get_keys_returns_tuple(config_file: Path) -> None:
    manager = KeyVaultManager(config_file)

    assert manager.get_keys() == ("k1", "k2")


def test_get_log_location_returns_configured_value(
    config_file: Path,
    valid_config_data: dict[str, object],
) -> None:
    manager = KeyVaultManager(config_file)

    assert manager.get_log_location() == valid_config_data["LogLocation"]


def test_reload_config(config_file: Path, valid_config_data: dict[str, object]) -> None:
    manager = KeyVaultManager(config_file)
    valid_config_data["KeyVaultURL"] = "https://updated.vault.azure.net/"
    valid_config_data["SecretsName"] = ["updated"]
    write_config(config_file, valid_config_data)

    manager.reload_config()

    assert manager.get_keyvault_url() == "https://updated.vault.azure.net/"
    assert manager.get_secret_names() == ("updated",)


def test_validate_config_returns_current_config(config_file: Path) -> None:
    manager = KeyVaultManager(config_file)

    assert manager.validate_config().keyvault_url == manager.get_keyvault_url()


def test_logger_creates_log_file(
    config_file: Path,
    valid_config_data: dict[str, object],
) -> None:
    KeyVaultManager(config_file)

    log_file = Path(str(valid_config_data["LogLocation"])) / get_log_file_name()
    assert log_file.is_file()


def test_validation_failure_is_logged(
    tmp_path: Path,
    valid_config_data: dict[str, object],
    caplog: pytest.LogCaptureFixture,
) -> None:
    valid_config_data["KeyVaultURL"] = ""
    config_file = tmp_path / "config.json"
    write_config(config_file, valid_config_data)

    with caplog.at_level(logging.ERROR), pytest.raises(InvalidConfigValueError):
        KeyVaultManager(config_file)

    assert "event=config_validation status=failure" in caplog.text


def test_logger_setup_error_is_logged_and_raised(
    config_file: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    def raise_logger_setup_error(log_location: str) -> logging.Logger:
        raise LoggerSetupError("test logger setup failure")

    monkeypatch.setattr(manager_module, "create_file_logger", raise_logger_setup_error)

    with caplog.at_level(logging.ERROR), pytest.raises(LoggerSetupError):
        KeyVaultManager(config_file)

    assert "event=logger_initialize_failed" in caplog.text


def test_json_root_list_raises_invalid_config_value(tmp_path: Path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text("[1, 2, 3]", encoding="utf-8")

    with pytest.raises(InvalidConfigValueError):
        KeyVaultManager(config_file)


def test_application_can_catch_base_exception(tmp_path: Path) -> None:
    with pytest.raises(KeyVaultLibraryError):
        KeyVaultManager(tmp_path / "missing.json")
