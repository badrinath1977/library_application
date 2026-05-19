from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from libraries.jwt_validation_library.jwt_validation.errors import JwtValidationError


@dataclass(frozen=True, slots=True)
class JwtValidationSuccess:
    claim_value: Any
    claims: dict[str, Any]


@dataclass(frozen=True, slots=True)
class JwtValidationResult:
    success: bool
    value: JwtValidationSuccess | None = None
    error: JwtValidationError | None = None

    @classmethod
    def ok(cls, claim_value: Any, claims: dict[str, Any]) -> JwtValidationResult:
        return cls(success=True, value=JwtValidationSuccess(claim_value, claims))

    @classmethod
    def fail(cls, error: JwtValidationError) -> JwtValidationResult:
        return cls(success=False, error=error)
