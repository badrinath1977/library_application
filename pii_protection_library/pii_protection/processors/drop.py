from __future__ import annotations

from pii_protection.models import PiiRequestContext, PiiRule
from pii_protection.processors.base import PiiActionResult


class DropActionProcessor:
    reversible = False

    def protect(
        self,
        original_value: str,
        rule: PiiRule,
        context: PiiRequestContext,
    ) -> PiiActionResult:
        del original_value, rule, context
        return PiiActionResult(protected_value=None, dropped=True)

    def restore(self, protected_value: str, rule: PiiRule, context: PiiRequestContext) -> str:
        del rule, context
        return protected_value
