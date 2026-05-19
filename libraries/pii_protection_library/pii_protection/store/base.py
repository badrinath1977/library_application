from __future__ import annotations

from typing import Protocol

from libraries.pii_protection_library.pii_protection.models import PiiMapping


class PiiMappingStore(Protocol):
    def save(self, correlation_id: str, token: str, mapping: PiiMapping) -> None:
        """Save a reversible PII mapping scoped by correlation ID."""

    def find(self, correlation_id: str, token: str) -> PiiMapping | None:
        """Find one reversible PII mapping."""

    def find_all(self, correlation_id: str) -> list[PiiMapping]:
        """Find all mappings scoped to a correlation ID."""

    def delete_by_correlation_id(self, correlation_id: str) -> None:
        """Delete all mappings for a correlation ID."""
