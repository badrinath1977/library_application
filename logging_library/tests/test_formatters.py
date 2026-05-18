import json

from enterprise_logging.core.types import LogLevel, LogRecord
from enterprise_logging.formatter.json_formatter import JsonFormatter
from enterprise_logging.formatter.text_formatter import TextFormatter


def _record() -> LogRecord:
    return LogRecord.create(
        level=LogLevel.INFO,
        message="hello",
        module="tests",
        application="app",
        environment="test",
        service="svc",
        hostname="host",
        process_id=1,
        thread_id=2,
        correlation_id="corr",
        request_id="req",
        version="1",
        metadata={"k": "v"},
        context={"tenant": "a"},
        error=None,
    )


def test_json_formatter_structures_required_fields() -> None:
    payload = json.loads(JsonFormatter().format(_record()))

    assert payload["timestamp"]
    assert payload["level"] == "INFO"
    assert payload["message"] == "hello"
    assert payload["module"] == "tests"
    assert payload["correlationId"] == "corr"
    assert payload["metadata"] == {"k": "v"}


def test_text_formatter_is_readable() -> None:
    text = TextFormatter().format(_record())

    assert "INFO" in text
    assert "app/svc" in text
    assert "correlationId=corr" in text
