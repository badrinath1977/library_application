from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

import jwt

from libraries.jwt_validation_library.jwt_validation.config import Claims, JwtValidatorConfig
from libraries.jwt_validation_library.jwt_validation.errors import (
    ExpiredTokenError,
    InsufficientRoleError,
    InsufficientScopeError,
    InvalidAudienceError,
    InvalidIssuerError,
    InvalidSignatureError,
    JwtErrorCode,
    JwtValidationError,
    MalformedTokenError,
    MissingClaimError,
    UnsupportedAlgorithmError,
)
from libraries.jwt_validation_library.jwt_validation.jwks import JwksKeyResolver
from libraries.jwt_validation_library.jwt_validation.result import JwtValidationResult, JwtValidationSuccess


class JwtValidator:
    def __init__(self, config: JwtValidatorConfig) -> None:
        self._config = config
        self._resolver = JwksKeyResolver(config)

    def validate(self, token: str) -> JwtValidationResult:
        try:
            claims = self._validate_or_raise(token)
            return_claim = self._config.return_claim
            if return_claim not in claims:
                raise MissingClaimError(return_claim)
            return JwtValidationResult.ok(claim_value=claims[return_claim], claims=dict(claims))
        except JwtValidationError as error:
            return JwtValidationResult.fail(error)

    def validate_or_raise(self, token: str) -> JwtValidationSuccess:
        result = self.validate(token)
        if result.success and result.value is not None:
            return result.value
        if result.error is not None:
            raise result.error
        raise JwtValidationError(JwtErrorCode.MALFORMED_TOKEN, "JWT validation failed")

    def _validate_or_raise(self, token: str) -> dict[str, Any]:
        headers = self._read_headers(token)
        algorithm = headers.get("alg")
        if not isinstance(algorithm, str) or algorithm.upper() == "NONE":
            raise UnsupportedAlgorithmError(algorithm if isinstance(algorithm, str) else None)
        if algorithm not in self._config.allowed_algorithms:
            raise UnsupportedAlgorithmError(algorithm)

        key = self._resolver.resolve_key(headers)
        try:
            claims = jwt.decode(
                token,
                key=key,
                algorithms=list(self._config.allowed_algorithms),
                issuer=self._config.issuer,
                audience=self._config.audience,
                leeway=self._config.clock_skew_seconds,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_nbf": True,
                    "verify_iat": True,
                    "verify_iss": self._config.issuer is not None,
                    "verify_aud": self._config.audience is not None,
                    "require": ["exp"],
                },
            )
        except jwt.ExpiredSignatureError as exc:
            raise ExpiredTokenError() from exc
        except jwt.InvalidSignatureError as exc:
            raise InvalidSignatureError() from exc
        except jwt.InvalidIssuerError as exc:
            raise InvalidIssuerError() from exc
        except jwt.InvalidAudienceError as exc:
            raise InvalidAudienceError() from exc
        except jwt.MissingRequiredClaimError as exc:
            raise MissingClaimError(exc.claim) from exc
        except jwt.ImmatureSignatureError as exc:
            raise JwtValidationError(
                JwtErrorCode.TOKEN_NOT_YET_VALID,
                "JWT is not yet valid",
            ) from exc
        except jwt.InvalidTokenError as exc:
            raise MalformedTokenError(str(exc)) from exc

        self._validate_subject(claims)
        self._validate_required_scopes(claims)
        self._validate_required_roles(claims)
        self._run_custom_validators(claims)
        return dict(claims)

    @staticmethod
    def _read_headers(token: str) -> dict[str, Any]:
        try:
            headers = jwt.get_unverified_header(token)
        except jwt.DecodeError as exc:
            raise MalformedTokenError() from exc
        if not isinstance(headers, dict):
            raise MalformedTokenError()
        return headers

    def _validate_subject(self, claims: Claims) -> None:
        if self._config.subject is not None and claims.get("sub") != self._config.subject:
            raise JwtValidationError(
                JwtErrorCode.INVALID_CLAIM,
                "JWT subject is invalid",
                claim="sub",
            )

    def _validate_required_scopes(self, claims: Claims) -> None:
        if not self._config.required_scopes:
            return
        present = _extract_values(claims, self._config.scope_claim_names)
        missing = self._config.required_scopes - present
        if missing:
            raise InsufficientScopeError(missing)

    def _validate_required_roles(self, claims: Claims) -> None:
        if not self._config.required_roles:
            return
        present = _extract_values(claims, self._config.role_claim_names)
        missing = self._config.required_roles - present
        if missing:
            raise InsufficientRoleError(missing)

    def _run_custom_validators(self, claims: Claims) -> None:
        for validator in self._config.custom_claim_validators:
            try:
                is_valid = validator.validate(claims)
            except Exception as exc:
                raise JwtValidationError(
                    JwtErrorCode.INVALID_CLAIM,
                    validator.error_message or f"Custom claim validator failed: {validator.name}",
                ) from exc
            if not is_valid:
                raise JwtValidationError(
                    JwtErrorCode.INVALID_CLAIM,
                    validator.error_message
                    or f"Custom claim validator rejected token: {validator.name}",
                )


def _extract_values(claims: Mapping[str, Any], claim_names: Iterable[str]) -> set[str]:
    values: set[str] = set()
    for claim_name in claim_names:
        raw_value = claims.get(claim_name)
        if raw_value is None:
            continue
        if isinstance(raw_value, str):
            values.update(item for item in raw_value.split() if item)
        elif isinstance(raw_value, Iterable):
            values.update(str(item) for item in raw_value)
    return values
