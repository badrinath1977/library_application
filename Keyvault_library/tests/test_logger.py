"""Tests for logging setup."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from keyvault_library.exceptions import LoggerSetupError
from keyvault_library.logger import (
    create_file_logger,
    get_bootstrap_logger,
    get_log_file_name,
)


def test_logger_creates_log_file(tmp_path: Path) -> None:
    logger = create_file_logger(tmp_path)
    logger.info("event=test status=success")

    log_file = tmp_path / get_log_file_name()
    assert log_file.is_file()
    assert "event=test status=success" in log_file.read_text(encoding="utf-8")


def test_logger_avoids_duplicate_handlers(tmp_path: Path) -> None:
    logger = create_file_logger(tmp_path)

    assert len(logger.handlers) == 1


def test_logger_supports_required_levels(tmp_path: Path) -> None:
    logger = create_file_logger(tmp_path)

    assert logger.isEnabledFor(logging.DEBUG)
    assert logger.isEnabledFor(logging.INFO)
    assert logger.isEnabledFor(logging.WARNING)
    assert logger.isEnabledFor(logging.ERROR)
    assert logger.isEnabledFor(logging.CRITICAL)


def test_logger_setup_error_is_raised_for_invalid_location(
    tmp_path: Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    invalid_location = tmp_path / "file-not-directory"
    invalid_location.write_text("content", encoding="utf-8")

    with caplog.at_level(logging.ERROR), pytest.raises(LoggerSetupError):
        create_file_logger(invalid_location)

    assert "event=logger_setup_failed" in caplog.text


def test_bootstrap_logger_uses_single_null_handler() -> None:
    logger = get_bootstrap_logger()
    before_count = len(logger.handlers)
    get_bootstrap_logger()

    assert len(logger.handlers) == before_count

