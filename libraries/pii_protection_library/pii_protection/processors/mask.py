from __future__ import annotations

from libraries.pii_protection_library.pii_protection.models import PiiRequestContext, PiiRule
from libraries.pii_protection_library.pii_protection.processors.base import PiiActionResult


class MaskActionProcessor:
    reversible = False

    def protect(
        self,
        original_value: str,
        rule: PiiRule,
        context: PiiRequestContext,
    ) -> PiiActionResult:
        del context
        params = rule.action.params
        mask_char = str(params.get("maskChar", "*"))
        preserve_length = bool(params.get("preserveLength", False))
        mask_length = len(original_value) if preserve_length else int(params.get("maskLength", 8))
        return PiiActionResult(protected_value=mask_char * max(mask_length, 0))

    def restore(self, protected_value: str, rule: PiiRule, context: PiiRequestContext) -> str:
        del rule, context
        return protected_value
