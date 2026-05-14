"""Validation helpers for keyvault_library configuration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from keyvault_library.exceptions import (
    InvalidConfigValueError,
    MissingConfigKeyError,
)
from keyvault_library.models import KeyVaultConfig

KEYVAULT_URL = "KeyVaultURL"
SECRETS_NAME = "SecretsName"
KEY = "Key"
LOG_LOCATION = "LogLocation"

REQUIRED_CONFIG_KEYS: tuple[str, ...] = (
    KEYVAULT_URL,
    SECRETS_NAME,
    KEY,
    LOG_LOCATION,
)


def validate_config_payload(payload: Mapping[str, Any]) -> KeyVaultConfig:
    """Validate a raw configuration payload.

    Args:
        payload: JSON object loaded from ``config.json``.

    Returns:
        Immutable validated configuration.

    Raises:
        MissingConfigKeyError: If a required key is absent.
        InvalidConfigValueError: If any value has an invalid type or value.
    """

    if not isinstance(payload, Mapping):
        raise InvalidConfigValueError("Configuration root must be a JSON object.")

    for key_name in REQUIRED_CONFIG_KEYS:
        if key_name not in payload:
            raise MissingConfigKeyError(
                f"Missing required configuration key: '{key_name}'."
            )

    return KeyVaultConfig(
        keyvault_url=validate_non_empty_string(payload[KEYVAULT_URL], KEYVAULT_URL),
        secret_names=validate_non_empty_string_list(
            payload[SECRETS_NAME],
            SECRETS_NAME,
        ),
        keys=validate_non_empty_string_list(payload[KEY], KEY),
        log_location=validate_non_empty_string(payload[LOG_LOCATION], LOG_LOCATION),
    )


def validate_non_empty_string(value: Any, key_name: str) -> str:
    """Validate that ``value`` is a non-empty string."""

    if not isinstance(value, str) or not value.strip():
        raise InvalidConfigValueError(
            f"Configuration key '{key_name}' must be a non-empty string."
        )
    return value


def validate_non_empty_string_list(value: Any, key_name: str) -> tuple[str, ...]:
    """Validate that ``value`` is a non-empty list of non-empty strings."""

    if not isinstance(value, list):
        raise InvalidConfigValueError(
            f"Configuration key '{key_name}' must be a list of strings."
        )

    if not value:
        raise InvalidConfigValueError(
            f"Configuration key '{key_name}' must not be an empty list."
        )

    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise InvalidConfigValueError(
            f"Configuration key '{key_name}' must contain only non-empty strings."
        )

    return tuple(value)

