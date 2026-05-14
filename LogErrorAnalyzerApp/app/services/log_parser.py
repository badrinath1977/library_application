"""Extensible multi-language log parser."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class ParsedError:
    """Parsed raw error occurrence."""

    id: str
    error_message: str | None
    exception_type: str | None
    stacktrace: str
    method_name: str | None
    file_name: str | None
    line_number: int | None
    class_name: str | None
    module_name: str | None
    timestamp: str | None
    log_level: str | None
    raw_error_block: str
    source_file: str


TIMESTAMP_PATTERN = re.compile(
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?)"
)
LEVEL_PATTERN = re.compile(r"\b(DEBUG|INFO|WARN|WARNING|ERROR|CRITICAL|FATAL)\b")
PY_EXCEPTION_PATTERN = re.compile(r"^(?P<type>[A-Za-z_][\w.]*Error|Exception):?\s*(?P<msg>.*)$")
JAVA_EXCEPTION_PATTERN = re.compile(r"(?P<type>[\w.$]+(?:Exception|Error)):\s*(?P<msg>.*)")
DOTNET_EXCEPTION_PATTERN = re.compile(r"(?P<type>[\w.]+Exception):\s*(?P<msg>.*)")
NODE_EXCEPTION_PATTERN = re.compile(r"(?P<type>[A-Za-z_][\w]*Error):\s*(?P<msg>.*)")
PY_FRAME_PATTERN = re.compile(r'File "(?P<file>[^"]+)", line (?P<line>\d+), in (?P<method>[\w<>]+)')
JAVA_FRAME_PATTERN = re.compile(
    r"\s*at (?P<class>[\w.$]+)\.(?P<method>[\w$<>]+)\((?P<file>[^:()]+)(?::(?P<line>\d+))?\)"
)
DOTNET_FRAME_PATTERN = re.compile(
    r"\s*at (?P<class>[\w.]+)\.(?P<method>[\w<>]+)\(.*\) in (?P<file>.*):line (?P<line>\d+)"
)
NODE_FRAME_PATTERN = re.compile(
    r"\s*at (?:(?P<method>[\w.<>]+) )?\(?(?P<file>[^():]+):(?P<line>\d+):\d+\)?"
)


class LogParser:
    """Parse log content into error occurrences."""

    def parse(self, content: str, source_file: Path) -> list[ParsedError]:
        """Parse all error blocks from file content."""

        blocks = self._split_error_blocks(content)
        return [self._parse_block(block, source_file) for block in blocks]

    def _split_error_blocks(self, content: str) -> list[str]:
        lines = content.splitlines()
        blocks: list[list[str]] = []
        current: list[str] = []
        in_error = False

        for line in lines:
            starts_error = self._looks_like_error_start(line)
            starts_new_log = bool(TIMESTAMP_PATTERN.search(line) and LEVEL_PATTERN.search(line))
            if starts_error and (not in_error or starts_new_log):
                if current:
                    blocks.append(current)
                current = [line]
                in_error = True
                continue
            if in_error:
                if starts_new_log and not self._looks_like_stack_line(line):
                    blocks.append(current)
                    current = []
                    in_error = False
                else:
                    current.append(line)
        if current:
            blocks.append(current)
        return ["\n".join(block).strip() for block in blocks if "\n".join(block).strip()]

    def _looks_like_error_start(self, line: str) -> bool:
        return bool(
            re.search(r"\b(ERROR|CRITICAL|FATAL|Exception|Traceback|Error:)\b", line)
        )

    def _looks_like_stack_line(self, line: str) -> bool:
        return bool(
            line.startswith(("Traceback", "  File ", "    at ", "   at ", "at "))
            or JAVA_FRAME_PATTERN.search(line)
            or DOTNET_FRAME_PATTERN.search(line)
            or NODE_FRAME_PATTERN.search(line)
        )

    def _parse_block(self, block: str, source_file: Path) -> ParsedError:
        exception_type, message = self._extract_exception(block)
        frame = self._extract_frame(block)
        timestamp_match = TIMESTAMP_PATTERN.search(block)
        level_match = LEVEL_PATTERN.search(block)
        normalized_key = f"{exception_type}|{message}|{frame.get('file')}|{frame.get('line')}"
        error_id = hashlib.sha256(normalized_key.encode("utf-8")).hexdigest()[:16]

        return ParsedError(
            id=error_id,
            error_message=message,
            exception_type=exception_type,
            stacktrace=block,
            method_name=frame.get("method"),
            file_name=frame.get("file"),
            line_number=int(frame["line"]) if frame.get("line") else None,
            class_name=frame.get("class"),
            module_name=_module_from_file(frame.get("file")),
            timestamp=timestamp_match.group("timestamp") if timestamp_match else None,
            log_level=level_match.group(1) if level_match else None,
            raw_error_block=block,
            source_file=str(source_file),
        )

    def _extract_exception(self, block: str) -> tuple[str | None, str | None]:
        for line in reversed(block.splitlines()):
            stripped = line.strip()
            for pattern in (
                JAVA_EXCEPTION_PATTERN,
                DOTNET_EXCEPTION_PATTERN,
                NODE_EXCEPTION_PATTERN,
                PY_EXCEPTION_PATTERN,
            ):
                match = pattern.search(stripped)
                if match:
                    return match.group("type"), match.group("msg").strip() or stripped
        first_line = block.splitlines()[0].strip() if block.splitlines() else None
        return None, first_line

    def _extract_frame(self, block: str) -> dict[str, str]:
        for line in block.splitlines():
            for pattern in (
                PY_FRAME_PATTERN,
                JAVA_FRAME_PATTERN,
                DOTNET_FRAME_PATTERN,
                NODE_FRAME_PATTERN,
            ):
                match = pattern.search(line)
                if match:
                    return {key: value for key, value in match.groupdict().items() if value}
        return {}


def _module_from_file(file_name: str | None) -> str | None:
    if not file_name:
        return None
    path = Path(file_name)
    if path.suffix:
        return path.stem
    return None

