from __future__ import annotations

from typing import Any

from pii_protection import PiiProtectionService, PiiRequestContext


PII_LOG_CONFIG: dict[str, Any] = {
    "application": "AbsenceAPI",
    "version": "1.0",
    "restorePolicy": {"enabled": False, "allowedRoles": [], "requireReason": False, "audit": False},
    "rules": [
        {"name": "person-number", "jsonPath": "$..personNumber", "type": "USERNAME", "regex": "^.*$", "action": {"type": "REDACT", "restore": False}},
        {"name": "person-id", "jsonPath": "$..personId", "type": "CUSTOM", "regex": "^.*$", "action": {"type": "REDACT", "restore": False}},
        {"name": "comments", "jsonPath": "$..comments", "type": "FREE_TEXT", "regex": "^.*$", "action": {"type": "PARTIAL_MASK", "restore": False, "params": {"visibleFirst": 24, "visibleLast": 0}}},
        {"name": "created-by", "jsonPath": "$..createdBy", "type": "EMAIL", "regex": "^.*$", "action": {"type": "REDACT", "restore": False}},
        {"name": "last-updated-by", "jsonPath": "$..lastUpdatedBy", "type": "EMAIL", "regex": "^.*$", "action": {"type": "REDACT", "restore": False}},
        {"name": "authorization", "jsonPath": "$..Authorization", "type": "ACCESS_TOKEN", "regex": "^.*$", "action": {"type": "REDACT", "restore": False}},
    ],
}

_service = PiiProtectionService()


def mask_for_log(payload: Any, trace_id: str | None = None) -> Any:
    try:
        result = _service.protect(
            payload,
            PII_LOG_CONFIG,
            PiiRequestContext(application="AbsenceAPI", correlationId=trace_id or "log"),
        )
        return result.protected_payload
    except Exception:  # noqa: BLE001
        return {"masked": True}

