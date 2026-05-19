from __future__ import annotations

from typing import Any

from pii_protection import PiiProtectionService, PiiRequestContext


PII_LOG_CONFIG: dict[str, Any] = {
    "application": "ChatAPI",
    "version": "1.0",
    "restorePolicy": {"enabled": False, "allowedRoles": [], "requireReason": False, "audit": False},
    "rules": [
        {"name": "user-id", "jsonPath": "$..userId", "type": "USERNAME", "regex": "^.*$", "action": {"type": "REDACT", "restore": False}},
        {"name": "message", "jsonPath": "$..message", "type": "FREE_TEXT", "regex": "^.*$", "action": {"type": "PARTIAL_MASK", "restore": False, "params": {"visibleFirst": 32, "visibleLast": 0}}},
        {"name": "authorization", "jsonPath": "$..Authorization", "type": "ACCESS_TOKEN", "regex": "^.*$", "action": {"type": "REDACT", "restore": False}},
        {"name": "token", "jsonPath": "$..token", "type": "ACCESS_TOKEN", "regex": "^.*$", "action": {"type": "REDACT", "restore": False}},
        {"name": "secret", "jsonPath": "$..secret", "type": "API_KEY", "regex": "^.*$", "action": {"type": "REDACT", "restore": False}},
    ],
}

_service = PiiProtectionService()


def mask_for_log(payload: Any, trace_id: str | None = None) -> Any:
    try:
        result = _service.protect(
            payload,
            PII_LOG_CONFIG,
            PiiRequestContext(application="ChatAPI", correlationId=trace_id or "log"),
        )
        return result.protected_payload
    except Exception:  # noqa: BLE001
        return {"masked": True}

