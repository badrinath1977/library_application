from __future__ import annotations

import dataclasses
import traceback
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import Any

from enterprise_logging.core.types import ErrorInfo


class SafeSerializer:
    def __init__(self, *, max_depth: int = 20, max_items: int = 1000) -> None:
        self.max_depth = max_depth
        self.max_items = max_items

    def serialize(self, value: Any) -> Any:
        return self._serialize(value, depth=0, seen=set())

    def error(self, exc: BaseException) -> ErrorInfo:
        cause = exc.__cause__ or exc.__context__
        attrs = {
            key: self.serialize(value)
            for key, value in getattr(exc, "__dict__", {}).items()
            if not key.startswith("_")
        }
        return ErrorInfo(
            type=exc.__class__.__name__,
            message=str(exc),
            stack="".join(traceback.format_exception(type(exc), exc, exc.__traceback__)),
            cause=self.error(cause) if cause else None,
            attributes=attrs,
        )

    def _serialize(self, value: Any, *, depth: int, seen: set[int]) -> Any:
        if depth > self.max_depth:
            return "[MaxDepthExceeded]"
        if value is None or isinstance(value, str | int | float | bool):
            return value
        if isinstance(value, datetime | date):
            return value.isoformat()
        if isinstance(value, Enum):
            return value.name
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, BaseException):
            return dataclasses.asdict(self.error(value))

        value_id = id(value)
        if value_id in seen:
            return "[CircularReference]"
        seen.add(value_id)
        try:
            if dataclasses.is_dataclass(value) and not isinstance(value, type):
                return self._serialize(dataclasses.asdict(value), depth=depth + 1, seen=seen)
            if isinstance(value, Mapping):
                output: dict[str, Any] = {}
                for index, (key, item) in enumerate(value.items()):
                    if index >= self.max_items:
                        output["[Truncated]"] = f"Exceeded {self.max_items} items"
                        break
                    output[str(key)] = self._serialize(item, depth=depth + 1, seen=seen)
                return output
            if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
                output_list = []
                for index, item in enumerate(value):
                    if index >= self.max_items:
                        output_list.append(f"[Truncated after {self.max_items} items]")
                        break
                    output_list.append(self._serialize(item, depth=depth + 1, seen=seen))
                return output_list
            if hasattr(value, "__dict__"):
                return self._serialize(vars(value), depth=depth + 1, seen=seen)
            return repr(value)
        finally:
            seen.discard(value_id)
