from __future__ import annotations

from libraries.pii_protection_library.pii_protection.models import PiiRequestContext, PiiRule
from libraries.pii_protection_library.pii_protection.processors.base import PiiActionResult


class PartialMaskActionProcessor:
    reversible = False

    def protect(
        self,
        original_value: str,
        rule: PiiRule,
        context: PiiRequestContext,
    ) -> PiiActionResult:
        del context
        params = rule.action.params
        first = max(int(params.get("visibleFirst", 2)), 0)
        last = max(int(params.get("visibleLast", 2)), 0)
        mask_char = str(params.get("maskChar", "*"))
        if len(original_value) <= first + last:
            return PiiActionResult(protected_value=mask_char * len(original_value))
        return PiiActionResult(
            protected_value=(
                original_value[:first]
                + mask_char * (len(original_value) - first - last)
                + original_value[-last:]
            )
        )

    def restore(self, protected_value: str, rule: PiiRule, context: PiiRequestContext) -> str:
        del rule, context
        return protected_value
