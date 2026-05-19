"""Tests for logger setup."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest

from libraries.llm_platform_library.llm_platform_library.exceptions import LoggerSetupError
from libraries.llm_platform_library.llm_platform_library.logger import create_library_logger, get_log_file_name


def test_logger_file_creation(tmp_path: Path) -> None:
    logger = create_library_logger(tmp_path)
    logger.info("event=test_logger status=success")

    log_file = tmp_path / get_log_file_name()
    assert log_file.is_file()
    assert "event=test_logger status=success" in log_file.read_text(encoding="utf-8")


def test_logger_avoids_duplicate_handlers(tmp_path: Path) -> None:
    logger = create_library_logger(tmp_path)

    assert len(logger.handlers) == 1
    assert logger.isEnabledFor(logging.DEBUG)


def test_logger_setup_error_for_file_path(tmp_path: Path) -> None:
    invalid_location = tmp_path / "not-a-directory"
    invalid_location.write_text("content", encoding="utf-8")

    with pytest.raises(LoggerSetupError):
        create_library_logger(invalid_location)

