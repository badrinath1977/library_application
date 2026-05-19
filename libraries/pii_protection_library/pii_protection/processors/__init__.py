from __future__ import annotations

from libraries.pii_protection_library.pii_protection.crypto.key_provider import KeyProvider
from libraries.pii_protection_library.pii_protection.exceptions import PiiConfigError
from libraries.pii_protection_library.pii_protection.models import PiiActionType, PiiRequestContext, PiiRule
from libraries.pii_protection_library.pii_protection.processors.base import PiiActionProcessor, PiiActionResult
from libraries.pii_protection_library.pii_protection.processors.drop import DropActionProcessor
from libraries.pii_protection_library.pii_protection.processors.encrypt import EncryptActionProcessor
from libraries.pii_protection_library.pii_protection.processors.hash import HashActionProcessor
from libraries.pii_protection_library.pii_protection.processors.mask import MaskActionProcessor
from libraries.pii_protection_library.pii_protection.processors.partial_mask import PartialMaskActionProcessor
from libraries.pii_protection_library.pii_protection.processors.redact import RedactActionProcessor
from libraries.pii_protection_library.pii_protection.processors.tokenize import TokenGenerator, TokenizeActionProcessor


class FormatPreservingTokenizeProcessor(TokenizeActionProcessor):
    def protect(
        self,
        original_value: str,
        rule: PiiRule,
        context: PiiRequestContext,
    ) -> PiiActionResult:
        result = super().protect(original_value, rule, context)
        sequence = result.protected_value[-6:-2] if result.protected_value else "001"
        if rule.type.value == "EMAIL":
            protected = f"user_{sequence}@example.com"
        elif rule.type.value == "PHONE":
            protected = f"555000{sequence[-4:]}"
        else:
            protected = f"FPT_{rule.type.value}_{sequence}"
        return result.__class__(
            protected_value=protected,
            reversible=result.reversible,
            restore_allowed=result.restore_allowed,
            ttl_seconds=result.ttl_seconds,
        )


class PiiActionProcessorFactory:
    def __init__(
        self,
        key_provider: KeyProvider,
        token_generator: TokenGenerator | None = None,
    ) -> None:
        self.key_provider = key_provider
        self.token_generator = token_generator or TokenGenerator()

    def get_processor(self, action_type: PiiActionType) -> PiiActionProcessor:
        if action_type == PiiActionType.MASK:
            return MaskActionProcessor()
        if action_type == PiiActionType.PARTIAL_MASK:
            return PartialMaskActionProcessor()
        if action_type == PiiActionType.REDACT:
            return RedactActionProcessor()
        if action_type == PiiActionType.DROP:
            return DropActionProcessor()
        if action_type == PiiActionType.HASH:
            return HashActionProcessor(self.key_provider)
        if action_type == PiiActionType.TOKENIZE:
            return TokenizeActionProcessor(self.token_generator)
        if action_type == PiiActionType.ENCRYPT:
            return EncryptActionProcessor(self.key_provider)
        if action_type == PiiActionType.FORMAT_PRESERVING_TOKENIZE:
            return FormatPreservingTokenizeProcessor(self.token_generator)
        raise PiiConfigError(f"Unsupported action type: {action_type}")
