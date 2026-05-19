"""Smoke test for pii_protection installed from libraries-dist."""

from __future__ import annotations

import os

from pii_protection import InMemoryPiiMappingStore, PiiProtectionService


def run() -> str:
    os.environ.setdefault("PII_KEY_1", "local-encryption-key")
    os.environ.setdefault("PII_KEY_2", "local-hmac-key")
    config = {
        "application": "TestLibraryApp",
        "version": "1.0",
        "restorePolicy": {
            "enabled": True,
            "allowedRoles": ["PII_ADMIN"],
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
                "regex": "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$",
                "action": {
                    "type": "TOKENIZE",
                    "restore": True,
                    "params": {"tokenFormat": "{{PII_${type}_${sequence}}}"},
                },
            }
        ],
    }
    context = {
        "correlationId": "pii-smoke",
        "roles": {"PII_ADMIN"},
        "reason": "local library smoke test",
    }
    service = PiiProtectionService(mapping_store=InMemoryPiiMappingStore())
    protected = service.protect({"customer": {"email": "badri@gmail.com"}}, config, context)
    restored = service.restore(
        "LLM returned {{PII_EMAIL_001}}",
        protected.correlation_id,
        config,
        context,
    )
    return (
        "PASS pii_protection: "
        f"protected={protected.protected_payload['customer']['email']} "
        f"restored='{restored.restored_payload}'"
    )


if __name__ == "__main__":
    print(run())
