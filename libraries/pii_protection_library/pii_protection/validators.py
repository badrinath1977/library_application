from __future__ import annotations

import re

from libraries.pii_protection_library.pii_protection.exceptions import PiiConfigError


class RegexValidator:
    def validate(self, value: str, pattern: str | None) -> bool:
        if not pattern:
            return True
        try:
            return re.fullmatch(pattern, value) is not None
        except re.error as exc:
            raise PiiConfigError(f"Invalid regex pattern: {pattern}") from exc
