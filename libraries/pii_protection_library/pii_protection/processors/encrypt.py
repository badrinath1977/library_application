from __future__ import annotations

from libraries.pii_protection_library.pii_protection.crypto.aes_gcm import AesGcmCrypto
from libraries.pii_protection_library.pii_protection.crypto.key_provider import KeyProvider
from libraries.pii_protection_library.pii_protection.models import PiiRequestContext, PiiRule
from libraries.pii_protection_library.pii_protection.processors.base import PiiActionResult


class EncryptActionProcessor:
    reversible = True

    def __init__(self, key_provider: KeyProvider, crypto: AesGcmCrypto | None = None) -> None:
        self.key_provider = key_provider
        self.crypto = crypto or AesGcmCrypto()

    def protect(
        self,
        original_value: str,
        rule: PiiRule,
        context: PiiRequestContext,
    ) -> PiiActionResult:
        protected_value = self.crypto.encrypt(
            original_value,
            self.key_provider.encryption_key(context),
        )
        return PiiActionResult(
            protected_value=protected_value,
            reversible=True,
            restore_allowed=rule.action.restore,
        )

    def restore(self, protected_value: str, rule: PiiRule, context: PiiRequestContext) -> str:
        del rule
        return self.crypto.decrypt(protected_value, self.key_provider.encryption_key(context))
