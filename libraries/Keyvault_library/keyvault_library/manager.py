"""Main Key Vault configuration manager."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Self, TextIO

from libraries.Keyvault_library.keyvault_library.exceptions import (
    ConfigFileNotFoundError,
    InvalidConfigJsonError,
    InvalidConfigValueError,
    KeyVaultLibraryError,
    LoggerSetupError,
    MissingConfigKeyError,
)
from libraries.Keyvault_library.keyvault_library.logger import create_file_logger, get_bootstrap_logger
from libraries.Keyvault_library.keyvault_library.models import KeyVaultConfig
from libraries.Keyvault_library.keyvault_library.validators import validate_config_payload


class KeyVaultManager:
    """Load, validate, log, and expose Azure Key Vault configuration.

    The manager is intentionally focused on configuration metadata and safe
    application integration. Secret retrieval can be added later through Azure
    SDK adapters without changing this public API.
    """

    def __init__(self, config_path: str | Path = "config.json") -> None:
        self._config_path: Path | None = Path(config_path)
        self._logger = get_bootstrap_logger()
        self._logger.debug("event=manager_init_start")

        raw_config = self._load_json_config()
        self._config = self.validate_config(raw_config)
        self._logger = self._initialize_logger(self._config.log_location)
        self._logger.info(
            "event=config_load status=success config_path=%s",
            self._config_path,
        )
        self._logger.debug("event=manager_init_end")

    @classmethod
    def from_file(cls, config_path: str | Path) -> Self:
        """Create a manager by loading configuration from an explicit file path.

        This is the recommended constructor for production applications because
        the consuming application controls exactly which configuration file is
        loaded.
        """

        return cls(config_path)

    @classmethod
    def from_dict(cls, config_data: dict[str, Any]) -> Self:
        """Create a manager from application-owned configuration data.

        Use this when the consuming application already loads configuration
        from its own source, such as an application settings file, Azure App
        Configuration, environment-specific deployment config, or a centralized
        config service.
        """

        manager = cls.__new__(cls)
        manager._config_path = None
        manager._logger = get_bootstrap_logger()
        manager._logger.debug("event=manager_from_dict_start")
        manager._config = manager.validate_config(config_data)
        manager._logger = manager._initialize_logger(manager._config.log_location)
        manager._logger.info("event=config_load_from_dict status=success")
        manager._logger.debug("event=manager_from_dict_end")
        return manager

    @classmethod
    def from_env(cls, env_var_name: str = "KEYVAULT_LIBRARY_CONFIG") -> Self:
        """Create a manager from a config file path stored in an environment variable.

        Args:
            env_var_name: Environment variable containing the config file path.

        Raises:
            MissingConfigKeyError: If the environment variable is not set.
            InvalidConfigValueError: If the environment variable is empty.
        """

        logger = get_bootstrap_logger()
        logger.debug("event=manager_from_env_start env_var=%s", env_var_name)

        try:
            config_path = os.environ[env_var_name]
        except KeyError as exc:
            logger.exception(
                "event=config_env_missing status=failure env_var=%s",
                env_var_name,
            )
            raise MissingConfigKeyError(
                f"Environment variable '{env_var_name}' is required."
            ) from exc

        if not config_path.strip():
            try:
                raise InvalidConfigValueError(
                    f"Environment variable '{env_var_name}' must not be empty."
                )
            except InvalidConfigValueError:
                logger.exception(
                    "event=config_env_empty status=failure env_var=%s",
                    env_var_name,
                )
                raise

        logger.debug("event=manager_from_env_end env_var=%s", env_var_name)
        return cls.from_file(config_path)

    @property
    def config_path(self) -> Path | None:
        """Return the active configuration path, if file-backed."""

        return self._config_path

    def get_keyvault_url(self) -> str:
        """Return the configured Azure Key Vault URL."""

        self._logger.debug("event=get_keyvault_url_start")
        value = self._config.keyvault_url
        self._logger.debug("event=get_keyvault_url_end")
        return value

    def get_secret_names(self) -> tuple[str, ...]:
        """Return configured secret names as an immutable tuple."""

        self._logger.debug("event=get_secret_names_start")
        value = tuple(self._config.secret_names)
        self._logger.debug("event=get_secret_names_end count=%d", len(value))
        return value

    def get_keys(self) -> tuple[str, ...]:
        """Return configured keys as an immutable tuple."""

        self._logger.debug("event=get_keys_start")
        value = tuple(self._config.keys)
        self._logger.debug("event=get_keys_end count=%d", len(value))
        return value

    def get_log_location(self) -> str:
        """Return the configured log directory."""

        self._logger.debug("event=get_log_location_start")
        value = self._config.log_location
        self._logger.debug("event=get_log_location_end")
        return value

    def reload_config(self) -> None:
        """Reload configuration from disk and reinitialize file logging.

        Raises:
            KeyVaultLibraryError: If the manager was created from a dictionary
                and is not backed by a configuration file.
        """

        self._logger.debug("event=reload_config_start")
        if self._config_path is None:
            try:
                raise KeyVaultLibraryError(
                    "Cannot reload configuration because this manager was "
                    "created from in-memory configuration."
                )
            except KeyVaultLibraryError:
                self._logger.exception("event=reload_config_not_file_backed")
                raise

        raw_config = self._load_json_config()
        next_config = self.validate_config(raw_config)
        next_logger = self._initialize_logger(next_config.log_location)

        self._config = next_config
        self._logger = next_logger
        self._logger.info(
            "event=config_reload status=success config_path=%s",
            self._config_path,
        )
        self._logger.debug("event=reload_config_end")

    def validate_config(
        self,
        raw_config: dict[str, Any] | None = None,
    ) -> KeyVaultConfig:
        """Validate configuration and return an immutable model.

        Args:
            raw_config: Optional raw configuration. If omitted, the currently
                loaded configuration model is returned.
        """

        self._logger.debug("event=validate_config_start")

        if raw_config is None:
            self._logger.info("event=config_validation status=success")
            self._logger.debug("event=validate_config_end")
            return self._config

        try:
            config = validate_config_payload(raw_config)
            self._logger.info("event=config_validation status=success")
            self._logger.debug("event=validate_config_end")
            return config
        except (MissingConfigKeyError, InvalidConfigValueError):
            self._logger.exception("event=config_validation status=failure")
            raise
        except (TypeError, ValueError) as exc:
            self._logger.exception("event=config_validation status=unexpected_failure")
            raise InvalidConfigValueError("Configuration validation failed.") from exc

    def _load_json_config(self) -> dict[str, Any]:
        """Load and parse JSON configuration with custom exception handling."""

        if self._config_path is None:
            raise KeyVaultLibraryError("Configuration path is not available.")

        self._logger.debug("event=config_read_start path=%s", self._config_path)

        try:
            with self._config_path.open("r", encoding="utf-8") as config_file:
                payload = self._parse_json(config_file)
        except FileNotFoundError as exc:
            self._logger.exception(
                "event=config_file_missing status=failure path=%s",
                self._config_path,
            )
            raise ConfigFileNotFoundError(
                f"Configuration file was not found: '{self._config_path}'."
            ) from exc
        except PermissionError as exc:
            self._logger.exception(
                "event=config_file_permission_denied status=failure path=%s",
                self._config_path,
            )
            raise KeyVaultLibraryError(
                "Configuration file could not be read due to permissions."
            ) from exc
        except OSError as exc:
            self._logger.exception(
                "event=config_file_read_failed status=failure path=%s",
                self._config_path,
            )
            raise KeyVaultLibraryError("Configuration file could not be read.") from exc

        self._logger.debug("event=config_read_end path=%s", self._config_path)
        return payload

    def _parse_json(self, config_file: TextIO) -> dict[str, Any]:
        """Parse a config file object as JSON."""

        try:
            payload = json.load(config_file)
        except json.JSONDecodeError as exc:
            self._logger.exception(
                "event=config_json_invalid status=failure path=%s",
                self._config_path,
            )
            raise InvalidConfigJsonError(
                f"Configuration file contains invalid JSON: '{self._config_path}'."
            ) from exc

        if not isinstance(payload, dict):
            self._logger.error(
                "event=config_json_root_invalid status=failure path=%s",
                self._config_path,
            )
            raise InvalidConfigValueError("Configuration root must be a JSON object.")

        return payload

    def _initialize_logger(self, log_location: str) -> logging.Logger:
        """Create the file logger with protected error handling."""

        self._logger.debug("event=logger_initialize_start")

        try:
            logger = create_file_logger(log_location)
        except LoggerSetupError:
            self._logger.exception("event=logger_initialize_failed")
            raise

        logger.debug("event=logger_initialize_end")
        return logger
