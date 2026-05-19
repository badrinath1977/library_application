"""Tests for configuration validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from libraries.Keyvault_library.keyvault_library.exceptions import (
    InvalidConfigValueError,
    MissingConfigKeyError,
)
from libraries.Keyvault_library.keyvault_library.validators import validate_config_payload


@pytest.fixture
def valid_payload(tmp_path: Path) -> dict[str, object]:
    return {
        "KeyVaultURL": "https://testingkeyvalut.vault.azure.net/",
        "SecretsName": ["sec1", "sec2", "sec3"],
        "Key": ["k1", "k2"],
        "LogLocation": str(tmp_path / "logs"),
    }


def test_valid_payload_returns_immutable_config(
    valid_payload: dict[str, object],
) -> None:
    config = validate_config_payload(valid_payload)

    assert config.keyvault_url == "https://testingkeyvalut.vault.azure.net/"
    assert config.secret_names == ("sec1", "sec2", "sec3")
    assert config.keys == ("k1", "k2")


@pytest.mark.parametrize(
    "missing_key",
    ["KeyVaultURL", "SecretsName", "Key", "LogLocation"],
)
def test_missing_required_key_raises_missing_config_key_error(
    valid_payload: dict[str, object],
    missing_key: str,
) -> None:
    valid_payload.pop(missing_key)

    with pytest.raises(MissingConfigKeyError):
        validate_config_payload(valid_payload)


@pytest.mark.parametrize(
    ("key_name", "value"),
    [
        ("KeyVaultURL", ""),
        ("KeyVaultURL", "   "),
        ("KeyVaultURL", 123),
        ("SecretsName", []),
        ("SecretsName", "sec1"),
        ("SecretsName", ["sec1", ""]),
        ("SecretsName", ["sec1", None]),
        ("Key", []),
        ("Key", "k1"),
        ("Key", ["k1", ""]),
        ("Key", ["k1", None]),
        ("LogLocation", ""),
        ("LogLocation", "   "),
        ("LogLocation", None),
    ],
)
def test_invalid_value_raises_invalid_config_value_error(
    valid_payload: dict[str, object],
    key_name: str,
    value: object,
) -> None:
    valid_payload[key_name] = value

    with pytest.raises(InvalidConfigValueError):
        validate_config_payload(valid_payload)


def test_non_object_root_raises_invalid_config_value_error() -> None:
    with pytest.raises(InvalidConfigValueError):
        validate_config_payload(["bad"])  # type: ignore[arg-type]

