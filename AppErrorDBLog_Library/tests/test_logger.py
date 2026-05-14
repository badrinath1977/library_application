"""Tests for AppErrorLogger."""

from __future__ import annotations

import asyncio
from pathlib import Path

from app_error_db_log import AppErrorLogConfig, AppErrorLogger


class FakeCursor:
    def __init__(self) -> None:
        self.executed: list[tuple[str, tuple[object, ...]]] = []

    def execute(self, sql: str, params: tuple[object, ...]) -> None:
        self.executed.append((sql, params))


class FakeConnection:
    def __init__(self) -> None:
        self.cursor_obj = FakeCursor()
        self.committed = False
        self.closed = False

    def cursor(self) -> FakeCursor:
        return self.cursor_obj

    def commit(self) -> None:
        self.committed = True

    def close(self) -> None:
        self.closed = True


def test_log_exception_success(tmp_path: Path) -> None:
    fake_connection = FakeConnection()
    config = AppErrorLogConfig.from_dict(
        {
            "connection_string": "Driver=test",
            "fallback_file_path": str(tmp_path / "fallback.log"),
        }
    )
    logger = AppErrorLogger(
        config,
        connection_factory=lambda *_args, **_kw: fake_connection,
    )

    result = logger.log_exception(ValueError("bad"), module_name="Test")

    assert result.success is True
    assert fake_connection.committed is True


def test_log_exception_fallback(tmp_path: Path) -> None:
    fallback_path = tmp_path / "fallback.log"
    config = AppErrorLogConfig.from_dict(
        {
            "connection_string": "Driver=test",
            "fallback_file_path": str(fallback_path),
            "retry_count": 0,
        }
    )

    def fail_connection(*_args, **_kwargs):
        raise RuntimeError("db down")

    logger = AppErrorLogger(config, connection_factory=fail_connection)
    result = logger.log_exception(RuntimeError("boom"))

    assert result.used_fallback is True
    assert fallback_path.is_file()


def test_decorator_logs_and_reraises(tmp_path: Path) -> None:
    config = AppErrorLogConfig.from_dict(
        {
            "connection_string": "",
            "fallback_file_path": str(tmp_path / "fallback.log"),
        }
    )
    logger = AppErrorLogger(config)

    @logger.log_exceptions(module_name="Decorated")
    def fail() -> None:
        raise RuntimeError("bad")

    try:
        fail()
    except RuntimeError:
        pass
    else:
        raise AssertionError("Expected RuntimeError")


def test_context_manager_suppresses_when_configured(tmp_path: Path) -> None:
    config = AppErrorLogConfig.from_dict(
        {
            "connection_string": "",
            "fallback_file_path": str(tmp_path / "fallback.log"),
            "suppress_original_exception": True,
        }
    )
    logger = AppErrorLogger(config)

    with logger.capture(module_name="Context"):
        raise RuntimeError("bad")


def test_async_logging(tmp_path: Path) -> None:
    config = AppErrorLogConfig.from_dict(
        {
            "connection_string": "",
            "fallback_file_path": str(tmp_path / "fallback.log"),
            "retry_count": 0,
        }
    )
    logger = AppErrorLogger(config)

    result = asyncio.run(logger.log_exception_async(RuntimeError("async")))

    assert result.used_fallback is True
