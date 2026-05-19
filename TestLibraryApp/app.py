"""Run every local-library smoke test as a consumer application."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from library_tests import (
    test_app_error_db_log_library,
    test_enterprise_logging_library,
    test_jwt_validation_library,
    test_keyvault_library,
    test_llm_platform_library,
    test_pii_protection_library,
)


TESTS: tuple[Callable[[], str], ...] = (
    test_keyvault_library.run,
    test_app_error_db_log_library.run,
    test_llm_platform_library.run,
    test_enterprise_logging_library.run,
    test_jwt_validation_library.run,
    test_pii_protection_library.run,
)


def main() -> int:
    Path("logs").mkdir(exist_ok=True)
    print("TestLibraryApp all-library smoke test started")
    print(f"Working directory: {Path.cwd()}")
    for test in TESTS:
        print(test())
    print("All library smoke tests completed successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
