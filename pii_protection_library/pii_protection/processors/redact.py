from __future__ import annotations

from pii_protection.models import PiiRequestContext, PiiRule
from pii_protection.processors.base import PiiActionResult


class RedactActionProcessor:
    reversible = False

    def protect(
        self,
        original_value: str,
        rule: PiiRule,
        context: PiiRequestContext,
    ) -> PiiActionResult:
        del original_value, context
        label_format = str(rule.action.params.get("labelFormat", "<${type}_REDACTED>"))
        return PiiActionResult(protected_value=label_format.replace("${type}", rule.type.value))

    def restore(self, protected_value: str, rule: PiiRule, context: PiiRequestContext) -> str:
        del rule, context
        return protected_value
