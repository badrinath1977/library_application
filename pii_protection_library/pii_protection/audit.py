from __future__ import annotations

from typing import Any, Protocol

from pii_protection.models import PiiRequestContext


class AuditLogger(Protocol):
    def audit(
        self,
        event: str,
        context: PiiRequestContext,
        details: dict[str, Any],
    ) -> None:
        """Emit an audit event. Details must never contain raw PII."""


class NoOpAuditLogger:
    def audit(
        self,
        event: str,
        context: PiiRequestContext,
        details: dict[str, Any],
    ) -> None:
        del event, context, details
