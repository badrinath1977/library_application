from __future__ import annotations

from typing import Any

from pii_protection import PiiProtectionService, PiiRequestContext

from app.core.settings import Settings


PII_LOG_CONFIG: dict[str, Any] = {
    "application": "ConfigRegistryAPI",
    "version": "1.0",
    "restorePolicy": {"enabled": False, "allowedRoles": [], "requireReason": False, "audit": False},
    "rules": [
        {
            "name": "config-value",
            "jsonPath": "$..ConfigValue",
            "type": "CUSTOM",
            "regex": "^.*$",
            "action": {"type": "REDACT", "restore": False},
        },
        {
            "name": "authorization",
            "jsonPath": "$..Authorization",
            "type": "ACCESS_TOKEN",
            "regex": "^.*$",
            "action": {"type": "REDACT", "restore": False},
        },
    ],
}


_pii_service = PiiProtectionService()


def is_keyvault_reference(value: Any, settings: Settings) -> bool:
    if not isinstance(value, str):
        return False
    normalized = value.strip()
    return any(normalized.startswith(prefix) for prefix in settings.keyvault_ref_prefixes)


def mask_config_row(row: dict[str, Any], settings: Settings) -> dict[str, Any]:
    safe_row = dict(row)
    if bool(safe_row.get("IsSensitive")):
        safe_row["ConfigValue"] = settings.sensitive_response_mask
    elif is_keyvault_reference(safe_row.get("ConfigValue"), settings):
        safe_row["ConfigValue"] = "<KEYVAULT_SECRET_REF>"
    return safe_row


def protect_log_payload(payload: Any, correlation_id: str | None = None) -> Any:
    try:
        context = PiiRequestContext(
            application="ConfigRegistryAPI",
            correlationId=correlation_id or "log",
            roles=set(),
        )
        result = _pii_service.protect(payload, PII_LOG_CONFIG, context)
        return result.protected_payload
    except Exception:  # noqa: BLE001
        return {"masked": True, "reason": "pii_log_masking_failed"}
