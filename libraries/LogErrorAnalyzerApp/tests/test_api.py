"""API tests."""

from pathlib import Path

from fastapi.testclient import TestClient

from libraries.LogErrorAnalyzerApp.app.main import app


def test_health() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["keyvault"]["configured"] is True
    assert data["keyvault"]["secrets_count"] == 3


def test_analyze_log_file(tmp_path: Path) -> None:
    log_file = tmp_path / "app.log"
    log_file.write_text(
        """2026-05-13 10:15:22 ERROR Failed
Traceback (most recent call last):
  File "service.py", line 42, in process_payment
ZeroDivisionError: division by zero
""",
        encoding="utf-8",
    )
    client = TestClient(app)

    response = client.post(
        "/analyze-log",
        json={
            "path": str(log_file),
            "recursive": True,
            "call_llm": True,
            "create_ticket": True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["errors_found"] == 1
    assert data["errors"][0]["llm_solution"] is not None
    assert data["errors"][0]["ticket"]["created"] is True


def test_invalid_path_returns_400() -> None:
    client = TestClient(app)

    response = client.post("/analyze-log", json={"path": "missing.log"})

    assert response.status_code == 400
