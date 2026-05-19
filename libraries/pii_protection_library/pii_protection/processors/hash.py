from __future__ import annotations

import base64
import hashlib
import hmac

from libraries.pii_protection_library.pii_protection.crypto.key_provider import KeyProvider
from libraries.pii_protection_library.pii_protection.models import PiiRequestContext, PiiRule
from libraries.pii_protection_library.pii_protection.processors.base import PiiActionResult


class HashActionProcessor:
    reversible = False

    def __init__(self, key_provider: KeyProvider) -> None:
        self.key_provider = key_provider

    def protect(
        self,
        original_value: str,
        rule: PiiRule,
        context: PiiRequestContext,
    ) -> PiiActionResult:
        params = rule.action.params
        key = self.key_provider.hmac_key(context)
        digest = hmac.new(key, original_value.encode("utf-8"), hashlib.sha256).digest()
        if str(params.get("outputEncoding", "HEX")).upper() == "BASE64":
            encoded = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
        else:
            encoded = digest.hex()
        return PiiActionResult(protected_value=str(params.get("prefix", "hmac_")) + encoded)

    def restore(self, protected_value: str, rule: PiiRule, context: PiiRequestContext) -> str:
        del rule, context
        return protected_value
