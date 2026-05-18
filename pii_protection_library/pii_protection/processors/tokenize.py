from __future__ import annotations

from collections import defaultdict

from pii_protection.models import PiiRequestContext, PiiRule, PiiType
from pii_protection.processors.base import PiiActionResult


class TokenGenerator:
    def __init__(self) -> None:
        self._counters: dict[PiiType, int] = defaultdict(int)

    def next(self, pii_type: PiiType, token_format: str | None = None, prefix: str = "PII") -> str:
        self._counters[pii_type] += 1
        sequence = f"{self._counters[pii_type]:03d}"
        template = token_format or "{{PII_${type}_${sequence}}}"
        return (
            template.replace("${prefix}", prefix)
            .replace("${type}", pii_type.value)
            .replace("${sequence}", sequence)
        )


class TokenizeActionProcessor:
    reversible = True

    def __init__(self, token_generator: TokenGenerator | None = None) -> None:
        self.token_generator = token_generator or TokenGenerator()

    def protect(
        self,
        original_value: str,
        rule: PiiRule,
        context: PiiRequestContext,
    ) -> PiiActionResult:
        del original_value, context
        params = rule.action.params
        token = self.token_generator.next(
            rule.type,
            token_format=params.get("tokenFormat"),
            prefix=str(params.get("prefix", "PII")),
        )
        return PiiActionResult(
            protected_value=token,
            reversible=True,
            restore_allowed=rule.action.restore,
            ttl_seconds=int(params["ttlSeconds"]) if "ttlSeconds" in params else None,
        )

    def restore(self, protected_value: str, rule: PiiRule, context: PiiRequestContext) -> str:
        del rule, context
        return protected_value
