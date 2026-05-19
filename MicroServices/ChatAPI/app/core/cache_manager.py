from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class CacheEntry:
    value: Any
    expires_at: float


class TTLCache:
    def __init__(self, default_ttl_seconds: int) -> None:
        self._default_ttl_seconds = default_ttl_seconds
        self._entries: dict[str, CacheEntry] = {}

    def get(self, key: str) -> Any | None:
        entry = self._entries.get(key)
        if entry is None:
            return None
        if entry.expires_at <= time.time():
            self._entries.pop(key, None)
            return None
        return entry.value

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl_seconds
        self._entries[key] = CacheEntry(value=value, expires_at=time.time() + ttl)

    def invalidate(self, key: str) -> None:
        self._entries.pop(key, None)

    def invalidate_prefix(self, prefix: str) -> None:
        for key in list(self._entries):
            if key.startswith(prefix):
                self._entries.pop(key, None)

    def clear(self) -> None:
        self._entries.clear()

