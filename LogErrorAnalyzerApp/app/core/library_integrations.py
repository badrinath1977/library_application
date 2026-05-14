"""Integrations with reusable internal libraries."""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)
APP_ROOT = Path(__file__).resolve().parents[2]


@lru_cache
def get_keyvault_manager() -> Any | None:
    """Return configured KeyVaultManager, or None if unavailable."""

    settings = get_settings()
    try:
        from keyvault_library import KeyVaultManager
        from keyvault_library.exceptions import KeyVaultLibraryError
    except ImportError:
        logger.exception("keyvault-library package is not installed")
        return None

    try:
        return KeyVaultManager.from_file(_resolve_app_path(settings.keyvault_config_path))
    except KeyVaultLibraryError:
        logger.exception("Failed to initialize KeyVaultManager")
        return None


@lru_cache
def get_app_error_logger() -> Any | None:
    """Return configured AppErrorLogger, or None if unavailable."""

    settings = get_settings()
    try:
        from app_error_db_log import AppErrorLogger
    except ImportError:
        logger.exception("AppErrorDBLog_Library package is not installed")
        return None

    try:
        return AppErrorLogger.from_config_file(
            _resolve_app_path(settings.app_error_db_log_config_path),
            section="AppErrorDBLog",
        )
    except (OSError, ValueError):
        logger.exception("Failed to initialize AppErrorLogger")
        return None


def log_exception_to_db(
    exception: BaseException,
    *,
    module_name: str,
    request_path: str | None = None,
    additional_info: dict[str, Any] | None = None,
) -> None:
    """Log exception through AppErrorDBLog_Library without breaking the API."""

    app_error_logger = get_app_error_logger()
    if app_error_logger is None:
        return
    try:
        app_error_logger.log_exception(
            exception,
            module_name=module_name,
            request_path=request_path,
            additional_info=additional_info,
        )
    except Exception:
        logger.exception("AppErrorLogger failed unexpectedly")


def get_keyvault_status() -> dict[str, Any]:
    """Return safe Key Vault configuration status."""

    manager = get_keyvault_manager()
    if manager is None:
        return {"configured": False}
    return {
        "configured": True,
        "keyvault_url": manager.get_keyvault_url(),
        "secrets_count": len(manager.get_secret_names()),
        "keys_count": len(manager.get_keys()),
        "log_location": manager.get_log_location(),
    }


def _resolve_app_path(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return APP_ROOT / path
