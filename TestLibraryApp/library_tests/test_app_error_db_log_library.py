"""Smoke test for app_error_db_log installed from libraries-dist."""

from __future__ import annotations

from app_error_db_log import AppErrorLogConfig, AppErrorLogger


def run() -> str:
    config = AppErrorLogConfig(
        connection_string="",
        application_name="TestLibraryApp",
        fallback_file_path="logs/app_error_db_fallback.log",
        suppress_logger_errors=True,
    )
    logger = AppErrorLogger(config)
    result = logger.log_exception(
        RuntimeError("synthetic smoke-test exception"),
        module_name="TestLibraryApp",
        correlation_id="app-error-db-log-smoke",
    )
    return f"PASS app_error_db_log: success={result.success} fallback={result.used_fallback}"


if __name__ == "__main__":
    print(run())
