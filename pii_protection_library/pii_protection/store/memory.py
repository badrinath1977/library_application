from __future__ import annotations

import time
from threading import RLock

from pii_protection.models import PiiMapping


class InMemoryPiiMappingStore:
    def __init__(self) -> None:
        self._data: dict[str, dict[str, PiiMapping]] = {}
        self._lock = RLock()

    def save(self, correlation_id: str, token: str, mapping: PiiMapping) -> None:
        with self._lock:
            self._data.setdefault(correlation_id, {})[token] = mapping

    def find(self, correlation_id: str, token: str) -> PiiMapping | None:
        with self._lock:
            mapping = self._data.get(correlation_id, {}).get(token)
            if mapping is None:
                return None
            if mapping.expires_at is not None and time.time() > mapping.expires_at:
                self._data.get(correlation_id, {}).pop(token, None)
                return None
            return mapping

    def find_all(self, correlation_id: str) -> list[PiiMapping]:
        with self._lock:
            scoped = list(self._data.get(correlation_id, {}).values())
        return [
            mapping
            for mapping in scoped
            if mapping.expires_at is None or time.time() <= mapping.expires_at
        ]

    def delete_by_correlation_id(self, correlation_id: str) -> None:
        with self._lock:
            self._data.pop(correlation_id, None)
