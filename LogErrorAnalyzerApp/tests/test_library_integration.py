"""Integration tests for internal reusable libraries."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

import app.core.library_integrations as integrations
from app.main import app


def test_keyvault_library_and_error_db_logger_integration(tmp_path: Path) -> None:
    """Verify Keyvault_library and AppErrorDBLog_Library are used by the app."""

    fallback_log = Path("logs/app_error_db_fallback.log")
    previous_size = fallback_log.stat().st_size if fallback_log.exists() else 0

    integrations.get_keyvault_manager.cache_clear()
    integrations.get_app_error_logger.cache_clear()

    client = TestClient(app)

    health_response = client.get("/health")
    assert health_response.status_code == 200
    health_data = health_response.json()
    assert health_data["keyvault"]["configured"] is True
    assert health_data["keyvault"]["secrets_count"] == 3
    assert health_data["keyvault"]["keys_count"] == 2

    log_file = tmp_path / "sample.log"
    log_file.write_text(
        """2026-05-13 10:15:22 ERROR Payment failed
Traceback (most recent call last):
  File "service.py", line 42, in process_payment
ZeroDivisionError: division by zero
""",
        encoding="utf-8",
    )

    analyze_response = client.post(
        "/analyze-log",
        json={
            "path": str(log_file),
            "recursive": True,
            "call_llm": True,
            "create_ticket": True,
        },
    )
    assert analyze_response.status_code == 200
    analyze_data = analyze_response.json()
    assert analyze_data["summary"]["errors_found"] == 1
    assert analyze_data["errors"][0]["llm_solution"] is not None
    assert analyze_data["errors"][0]["ticket"]["created"] is True

    failure_response = client.post("/analyze-log", json={"path": "missing.log"})
    assert failure_response.status_code == 400
    assert fallback_log.is_file()
    assert fallback_log.stat().st_size > previous_size
    assert "AnalyzeLogRoute" in fallback_log.read_text(encoding="utf-8")
