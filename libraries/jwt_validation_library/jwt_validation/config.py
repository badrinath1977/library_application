from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

Claims = Mapping[str, Any]
ClaimValidator = Callable[[Claims], bool]


@dataclass(frozen=True, slots=True)
class CustomClaimValidator:
    name: str
    validate: ClaimValidator
    error_message: str | None = None


@dataclass(frozen=True, slots=True)
class JwtValidatorConfig:
    return_claim: str
    jwks_url: str | None = None
    static_public_key: str | bytes | None = None
    issuer: str | None = None
    audience: str | Iterable[str] | None = None
    subject: str | None = None
    required_scopes: frozenset[str] = field(default_factory=frozenset)
    required_roles: frozenset[str] = field(default_factory=frozenset)
    custom_claim_validators: tuple[CustomClaimValidator, ...] = ()
    allowed_algorithms: tuple[str, ...] = ("RS256",)
    clock_skew_seconds: int = 60
    jwks_cache_ttl_seconds: int = 300
    jwks_request_timeout_seconds: float = 5.0
    require_https_jwks: bool = True
    scope_claim_names: tuple[str, ...] = ("scope", "scp", "scopes")
    role_claim_names: tuple[str, ...] = ("roles", "role")

    def __post_init__(self) -> None:
        if not self.return_claim:
            raise ValueError("return_claim is required")
        if bool(self.jwks_url) == bool(self.static_public_key):
            raise ValueError("Configure exactly one of jwks_url or static_public_key")
        if not self.allowed_algorithms:
            raise ValueError("At least one allowed algorithm is required")
        normalized = {algorithm.upper() for algorithm in self.allowed_algorithms}
        if "NONE" in normalized:
            raise ValueError("alg=none is never allowed")
        if self.clock_skew_seconds < 0:
            raise ValueError("clock_skew_seconds must be >= 0")
        if self.jwks_cache_ttl_seconds < 0:
            raise ValueError("jwks_cache_ttl_seconds must be >= 0")
