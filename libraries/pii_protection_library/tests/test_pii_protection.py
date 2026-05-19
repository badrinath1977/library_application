from __future__ import annotations

import json
from typing import Any

import pytest

from libraries.pii_protection_library.pii_protection import (
    InMemoryPiiMappingStore,
    PiiConfigError,
    PiiProtectionService,
    PiiRequestContext,
    PiiRestoreDeniedError,
)


class CapturingAuditLogger:
    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, Any]]] = []

    def audit(self, event: str, context: PiiRequestContext, details: dict[str, Any]) -> None:
        del context
        self.events.append((event, details))


def base_config(action: dict[str, Any] | None = None, regex: str | None = None) -> dict[str, Any]:
    return {
        "application": "loan-service",
        "version": "1.0",
        "restorePolicy": {
            "enabled": True,
            "allowedRoles": ["PII_ADMIN", "SUPPORT_L2"],
            "requireReason": True,
            "audit": True,
        },
        "keyConfig": {
            "keyProvider": "ENV",
            "key1Ref": "PII_KEY_1",
            "key2Ref": "PII_KEY_2",
        },
        "rules": [
            {
                "name": "email",
                "jsonPath": "$.customer.email",
                "type": "EMAIL",
                "regex": regex or "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$",
                "action": action
                or {
                    "type": "TOKENIZE",
                    "restore": True,
                    "params": {"tokenFormat": "{{PII_${type}_${sequence}}}"},
                },
            }
        ],
    }


def context() -> dict[str, Any]:
    return {
        "correlationId": "corr-1",
        "userId": "user-1",
        "roles": {"PII_ADMIN"},
        "reason": "customer support",
    }


def service() -> PiiProtectionService:
    return PiiProtectionService(mapping_store=InMemoryPiiMappingStore())


def test_protect_email() -> None:
    result = service().protect(
        {"customer": {"email": "badri@gmail.com"}},
        base_config(),
        context(),
    )

    assert result.protected_payload["customer"]["email"] == "{{PII_EMAIL_001}}"
    assert result.pii_items[0].type == "EMAIL"


def test_restore_email() -> None:
    pii_service = service()
    protected = pii_service.protect(
        {"customer": {"email": "badri@gmail.com"}},
        base_config(),
        context(),
    )

    restored = pii_service.restore(
        "Customer can be contacted at {{PII_EMAIL_001}}",
        protected.correlation_id,
        base_config(),
        context(),
    )

    assert restored.restored_payload == "Customer can be contacted at badri@gmail.com"
    assert restored.restored_items[0].restored is True


def test_protect_nested_json() -> None:
    cfg = base_config()
    cfg["rules"][0]["jsonPath"] = "$.application.customer.profile.email"
    result = service().protect(
        {"application": {"customer": {"profile": {"email": "badri@gmail.com"}}}},
        cfg,
        context(),
    )

    assert (
        result.protected_payload["application"]["customer"]["profile"]["email"]
        == "{{PII_EMAIL_001}}"
    )


def test_unsupported_action() -> None:
    cfg = base_config({"type": "NOT_SUPPORTED", "restore": False})

    with pytest.raises(PiiConfigError):
        service().protect({"customer": {"email": "badri@gmail.com"}}, cfg, context())


def test_invalid_regex() -> None:
    cfg = base_config(regex="[")

    with pytest.raises(PiiConfigError):
        service().protect({"customer": {"email": "badri@gmail.com"}}, cfg, context())


def test_role_denied_during_restore() -> None:
    pii_service = service()
    protected = pii_service.protect(
        {"customer": {"email": "badri@gmail.com"}},
        base_config(),
        context(),
    )

    denied_context = dict(context())
    denied_context["roles"] = {"ANALYST"}
    with pytest.raises(PiiRestoreDeniedError):
        pii_service.restore(
            "{{PII_EMAIL_001}}",
            protected.correlation_id,
            base_config(),
            denied_context,
        )


def test_drop_action() -> None:
    result = service().protect(
        {"customer": {"email": "badri@gmail.com", "name": "Badri"}},
        base_config({"type": "DROP", "restore": False}),
        context(),
    )

    assert "email" not in result.protected_payload["customer"]


def test_hash_action(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PII_KEY_1", "key-one")
    monkeypatch.setenv("PII_KEY_2", "key-two")
    result = service().protect(
        {"customer": {"email": "badri@gmail.com"}},
        base_config({"type": "HASH", "restore": False, "params": {"prefix": "hmac_"}}),
        context(),
    )

    assert result.protected_payload["customer"]["email"].startswith("hmac_")
    assert "badri@gmail.com" not in json.dumps(result.protected_payload)


def test_tokenize_action() -> None:
    result = service().protect(
        {"customer": {"email": "badri@gmail.com"}},
        base_config({"type": "TOKENIZE", "restore": True}),
        context(),
    )

    assert result.protected_payload["customer"]["email"] == "{{PII_EMAIL_001}}"


def test_encrypt_action(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PII_KEY_1", "encryption-key")
    monkeypatch.setenv("PII_KEY_2", "hmac-key")
    pii_service = service()
    protected = pii_service.protect(
        {"customer": {"email": "badri@gmail.com"}},
        base_config({"type": "ENCRYPT", "restore": True}),
        context(),
    )
    encrypted = protected.protected_payload["customer"]["email"]

    assert encrypted.startswith("ENC(")
    restored = pii_service.restore(
        {"message": f"Email {encrypted}"},
        protected.correlation_id,
        base_config({"type": "ENCRYPT", "restore": True}),
        context(),
    )
    assert restored.restored_payload["message"] == "Email badri@gmail.com"


def test_no_raw_pii_in_audit_log() -> None:
    audit = CapturingAuditLogger()
    pii_service = PiiProtectionService(mapping_store=InMemoryPiiMappingStore(), audit_logger=audit)
    pii_service.protect({"customer": {"email": "badri@gmail.com"}}, base_config(), context())

    serialized = json.dumps(audit.events)
    assert "badri@gmail.com" not in serialized
    assert "pii.protect" in serialized
