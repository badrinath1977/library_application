from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from pii_protection.models import PiiRequestContext, PiiRule


@dataclass(frozen=True)
class PiiActionResult:
    protected_value: str | None
    dropped: bool = False
    reversible: bool = False
    restore_allowed: bool = False
    ttl_seconds: int | None = None


class PiiActionProcessor(Protocol):
    reversible: bool

    def protect(
        self,
        original_value: str,
        rule: PiiRule,
        context: PiiRequestContext,
    ) -> PiiActionResult:
        """Protect one scalar PII value."""

    def restore(
        self,
        protected_value: str,
        rule: PiiRule,
        context: PiiRequestContext,
    ) -> str:
        """Restore one scalar value when supported."""
