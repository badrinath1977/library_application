"""Tests for log parser."""

from pathlib import Path

from app.services.error_analyzer import ErrorAnalyzer
from app.services.log_parser import LogParser


def test_parse_python_stack_trace(tmp_path: Path) -> None:
    log_file = tmp_path / "app.log"
    content = """2026-05-13 10:15:22 ERROR Failed
Traceback (most recent call last):
  File "C:\\Apps\\payments\\service.py", line 42, in process_payment
    1 / 0
ZeroDivisionError: division by zero
"""

    errors = LogParser().parse(content, log_file)

    assert len(errors) == 1
    assert errors[0].exception_type == "ZeroDivisionError"
    assert errors[0].method_name == "process_payment"
    assert errors[0].line_number == 42


def test_parse_java_stack_trace(tmp_path: Path) -> None:
    log_file = tmp_path / "app.log"
    content = """2026-05-13 10:16:22 ERROR failed
java.lang.NullPointerException: bad
    at com.example.OrderService.save(OrderService.java:77)
"""

    errors = LogParser().parse(content, log_file)

    assert errors[0].exception_type == "java.lang.NullPointerException"
    assert errors[0].class_name == "com.example.OrderService"
    assert errors[0].line_number == 77


def test_group_duplicate_errors(tmp_path: Path) -> None:
    log_file = tmp_path / "app.log"
    content = """2026-05-13 10:15:22 ERROR Failed
Traceback (most recent call last):
  File "service.py", line 42, in process_payment
ZeroDivisionError: division by zero
2026-05-13 10:16:22 ERROR Failed
Traceback (most recent call last):
  File "service.py", line 42, in process_payment
ZeroDivisionError: division by zero
"""

    parsed = LogParser().parse(content, log_file)
    analyzed = ErrorAnalyzer().analyze(parsed)

    assert analyzed[0].occurrence_count == 2

