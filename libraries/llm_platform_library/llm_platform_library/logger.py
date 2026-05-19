"""Structured logging setup for llm_platform_library."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from libraries.llm_platform_library.llm_platform_library.exceptions import LoggerSetupError

LOGGER_NAMESPACE = "llm_platform_library"
LOG_FILE_PREFIX = "llm_platform_library"


def get_bootstrap_logger() -> logging.Logger:
    """Return a bootstrap logger used before file logging is configured."""

    logger = logging.getLogger(f"{LOGGER_NAMESPACE}.bootstrap")
    if not any(isinstance(handler, logging.NullHandler) for handler in logger.handlers):
        logger.addHandler(logging.NullHandler())
    return logger


def get_log_file_name() -> str:
    """Return the UTC-dated log file name."""

    return f"{LOG_FILE_PREFIX}_{datetime.now(UTC):%Y%m%d}.log"


def create_library_logger(log_location: str | Path) -> logging.Logger:
    """Create a structured file logger.

    Raises:
        LoggerSetupError: If log directory or file handler creation fails.
    """

    bootstrap_logger = get_bootstrap_logger()

    try:
        log_directory = Path(log_location)
        log_directory.mkdir(parents=True, exist_ok=True)

        log_file = log_directory / get_log_file_name()
        logger = logging.getLogger(f"{LOGGER_NAMESPACE}.{uuid4().hex}")
        logger.setLevel(logging.DEBUG)
        logger.propagate = True
        logger.handlers.clear()

        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(_build_formatter())
        logger.addHandler(handler)

        logger.debug("event=logger_created status=success log_file=%s", log_file)
        return logger
    except OSError as exc:
        bootstrap_logger.exception(
            "event=logger_setup_failed status=error log_location=%s",
            log_location,
        )
        raise LoggerSetupError(
            "Unable to initialize llm_platform_library logger."
        ) from exc
    except ValueError as exc:
        bootstrap_logger.exception(
            "event=logger_setup_invalid status=error log_location=%s",
            log_location,
        )
        raise LoggerSetupError(
            "Invalid llm_platform_library logger configuration."
        ) from exc


def _build_formatter() -> logging.Formatter:
    """Build an audit-friendly log formatter."""

    return logging.Formatter(
        fmt=(
            "%(asctime)sZ | level=%(levelname)s | logger=%(name)s | "
            "module=%(module)s | function=%(funcName)s | line=%(lineno)d | "
            "%(message)s"
        ),
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
