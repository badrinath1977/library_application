"""Smoke test for enterprise_logging installed from libraries-dist."""

from __future__ import annotations

from enterprise_logging import flush, get_logger, initialize_logger, shutdown


def run() -> str:
    initialize_logger(
        {
            "level": "INFO",
            "format": "json",
            "outputs": [{"type": "file", "path": "logs/enterprise_logging.log"}],
            "async": {"enabled": False},
            "metadata": {
                "application": "TestLibraryApp",
                "environment": "local",
                "service": "all-library-smoke",
            },
        }
    )
    logger = get_logger("TestLibraryApp")
    logger.info("enterprise.logging.smoke", {"email": "badri@gmail.com"})
    flush()
    shutdown()
    return "PASS enterprise_logging: wrote logs/enterprise_logging.log"


if __name__ == "__main__":
    print(run())
