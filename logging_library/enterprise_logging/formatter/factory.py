from __future__ import annotations

from enterprise_logging.config.schema import LogFormat
from enterprise_logging.core.contracts import Formatter
from enterprise_logging.formatter.json_formatter import JsonFormatter
from enterprise_logging.formatter.text_formatter import TextFormatter


def create_formatter(format_name: LogFormat, *, timestamp_format: str = "iso8601") -> Formatter:
    if format_name == "json":
        return JsonFormatter(timestamp_format=timestamp_format)
    if format_name == "text":
        return TextFormatter(colorize=False)
    if format_name == "pretty":
        return TextFormatter(colorize=True)
    raise ValueError(f"Unsupported formatter: {format_name}")
