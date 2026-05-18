from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class JwtErrorCode(StrEnum):
    EXPIRED_TOKEN = "expired_token"
    INVALID_SIGNATURE = "invalid_signature"
    MISSING_CLAIM = "missing_claim"
    INVALID_ISSUER = "invalid_issuer"
    INVALID_AUDIENCE = "invalid_audience"
    INSUFFICIENT_SCOPE = "insufficient_scope"
    INSUFFICIENT_ROLE = "insufficient_role"
    MALFORMED_TOKEN = "malformed_token"
    UNSUPPORTED_ALGORITHM = "unsupported_algorithm"
    TOKEN_NOT_YET_VALID = "token_not_yet_valid"
    INVALID_CLAIM = "invalid_claim"
    KEY_RESOLUTION_FAILED = "key_resolution_failed"


@dataclass(frozen=True, slots=True)
class JwtValidationError(Exception):
    code: JwtErrorCode
    message: str
    claim: str | None = None
    details: dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        return self.message


class ExpiredTokenError(JwtValidationError):
    def __init__(self, message: str = "JWT access token is expired") -> None:
        super().__init__(JwtErrorCode.EXPIRED_TOKEN, message)


class InvalidSignatureError(JwtValidationError):
    def __init__(self, message: str = "JWT signature is invalid") -> None:
        super().__init__(JwtErrorCode.INVALID_SIGNATURE, message)


class MissingClaimError(JwtValidationError):
    def __init__(self, claim: str, message: str | None = None) -> None:
        super().__init__(
            JwtErrorCode.MISSING_CLAIM,
            message or f"JWT is missing required claim: {claim}",
            claim=claim,
        )


class InvalidIssuerError(JwtValidationError):
    def __init__(self, message: str = "JWT issuer is invalid") -> None:
        super().__init__(JwtErrorCode.INVALID_ISSUER, message, claim="iss")


class InvalidAudienceError(JwtValidationError):
    def __init__(self, message: str = "JWT audience is invalid") -> None:
        super().__init__(JwtErrorCode.INVALID_AUDIENCE, message, claim="aud")


class InsufficientScopeError(JwtValidationError):
    def __init__(self, missing: set[str] | frozenset[str]) -> None:
        super().__init__(
            JwtErrorCode.INSUFFICIENT_SCOPE,
            f"JWT is missing required scope(s): {', '.join(sorted(missing))}",
            claim="scope",
            details={"missing": sorted(missing)},
        )


class InsufficientRoleError(JwtValidationError):
    def __init__(self, missing: set[str] | frozenset[str]) -> None:
        super().__init__(
            JwtErrorCode.INSUFFICIENT_ROLE,
            f"JWT is missing required role(s): {', '.join(sorted(missing))}",
            claim="roles",
            details={"missing": sorted(missing)},
        )


class MalformedTokenError(JwtValidationError):
    def __init__(self, message: str = "JWT is malformed") -> None:
        super().__init__(JwtErrorCode.MALFORMED_TOKEN, message)


class UnsupportedAlgorithmError(JwtValidationError):
    def __init__(self, algorithm: str | None) -> None:
        super().__init__(
            JwtErrorCode.UNSUPPORTED_ALGORITHM,
            f"JWT signing algorithm is not allowed: {algorithm or '<missing>'}",
            details={"algorithm": algorithm},
        )
