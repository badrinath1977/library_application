from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from re import Pattern
from typing import Any

from libraries.logging_library.enterprise_logging.config.schema import MaskingConfig


class SensitiveDataMasker:
    def __init__(self, config: MaskingConfig) -> None:
        self.config = config
        self._keys = {key.lower() for key in config.sensitive_keys}
        self._patterns: tuple[Pattern[str], ...] = tuple(
            re.compile(pattern) for pattern in config.sensitive_patterns
        )

    def mask(self, value: Any) -> Any:
        if not self.config.enabled:
            return value
        return self._mask(value, depth=0, seen=set(), parent_key=None)

    def _mask(self, value: Any, *, depth: int, seen: set[int], parent_key: str | None) -> Any:
        if parent_key and self._is_sensitive_key(parent_key):
            return self.config.mask
        if isinstance(value, str):
            return self._mask_string(value)
        if value is None or isinstance(value, int | float | bool):
            return value

        value_id = id(value)
        if value_id in seen:
            return "[CircularReference]"
        seen.add(value_id)
        try:
            if isinstance(value, Mapping):
                return {
                    str(key): self._mask(item, depth=depth + 1, seen=seen, parent_key=str(key))
                    for key, item in value.items()
                }
            if isinstance(value, Sequence) and not isinstance(value, str | bytes | bytearray):
                return [
                    self._mask(item, depth=depth + 1, seen=seen, parent_key=parent_key)
                    for item in value
                ]
            return value
        finally:
            seen.discard(value_id)

    def _is_sensitive_key(self, key: str) -> bool:
        normalized = key.lower().replace("_", "").replace("-", "")
        for sensitive_key in self._keys:
            candidate = sensitive_key.lower().replace("_", "").replace("-", "")
            if candidate == normalized or candidate in normalized:
                return True
        return False

    def _mask_string(self, value: str) -> str:
        masked = value
        for pattern in self._patterns:
            masked = pattern.sub(lambda match: f"{match.group(1)}{self.config.mask}", masked)
        return masked
