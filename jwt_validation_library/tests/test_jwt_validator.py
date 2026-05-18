from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from jwt.algorithms import RSAAlgorithm

from jwt_validation import (
    CustomClaimValidator,
    JwtErrorCode,
    JwtValidator,
    JwtValidatorConfig,
)


def _generate_key_pair() -> tuple[Any, str, dict[str, Any]]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    jwk = json.loads(RSAAlgorithm.to_jwk(public_key))
    return private_key, public_pem, jwk


PRIVATE_KEY, PUBLIC_KEY, PUBLIC_JWK = _generate_key_pair()
OTHER_PRIVATE_KEY, OTHER_PUBLIC_KEY, OTHER_PUBLIC_JWK = _generate_key_pair()


def _token(
    *,
    private_key: Any = PRIVATE_KEY,
    kid: str = "key-1",
    algorithm: str = "RS256",
    overrides: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(UTC)
    claims: dict[str, Any] = {
        "iss": "https://issuer.example.com",
        "aud": "api://orders",
        "sub": "user-123",
        "scope": "orders:read orders:write",
        "roles": ["admin", "operator"],
        "tenant": "tenant-a",
        "exp": now + timedelta(minutes=5),
        "nbf": now - timedelta(seconds=5),
        "iat": now,
    }
    claims.update(overrides or {})
    return jwt.encode(claims, private_key, algorithm=algorithm, headers={"kid": kid})


def _config(**overrides: Any) -> JwtValidatorConfig:
    values = {
        "static_public_key": PUBLIC_KEY,
        "issuer": "https://issuer.example.com",
        "audience": "api://orders",
        "return_claim": "sub",
        "allowed_algorithms": ("RS256",),
        "clock_skew_seconds": 30,
    }
    values.update(overrides)
    return JwtValidatorConfig(**values)


def test_valid_token_returns_configured_claim() -> None:
    result = JwtValidator(_config()).validate(_token())

    assert result.success is True
    assert result.value is not None
    assert result.value.claim_value == "user-123"


def test_expired_token_fails() -> None:
    result = JwtValidator(_config(clock_skew_seconds=0)).validate(
        _token(overrides={"exp": datetime.now(UTC) - timedelta(seconds=1)})
    )

    assert result.success is False
    assert result.error is not None
    assert result.error.code == JwtErrorCode.EXPIRED_TOKEN


def test_missing_configured_return_claim_fails() -> None:
    result = JwtValidator(_config(return_claim="email")).validate(_token())

    assert result.success is False
    assert result.error is not None
    assert result.error.code == JwtErrorCode.MISSING_CLAIM
    assert result.error.claim == "email"


def test_invalid_issuer_fails() -> None:
    result = JwtValidator(_config()).validate(_token(overrides={"iss": "https://bad.example.com"}))

    assert result.success is False
    assert result.error is not None
    assert result.error.code == JwtErrorCode.INVALID_ISSUER


def test_invalid_audience_fails() -> None:
    result = JwtValidator(_config()).validate(_token(overrides={"aud": "api://other"}))

    assert result.success is False
    assert result.error is not None
    assert result.error.code == JwtErrorCode.INVALID_AUDIENCE


def test_invalid_signature_fails() -> None:
    token = _token(private_key=OTHER_PRIVATE_KEY)
    result = JwtValidator(_config()).validate(token)

    assert result.success is False
    assert result.error is not None
    assert result.error.code == JwtErrorCode.INVALID_SIGNATURE


def test_unsupported_algorithm_fails_before_signature_validation() -> None:
    token = jwt.encode(
        {
            "sub": "user-123",
            "exp": datetime.now(UTC) + timedelta(minutes=5),
        },
        "not-a-real-signing-secret-but-long-enough-for-tests",
        algorithm="HS256",
    )

    result = JwtValidator(_config()).validate(token)

    assert result.success is False
    assert result.error is not None
    assert result.error.code == JwtErrorCode.UNSUPPORTED_ALGORITHM


def test_unsigned_token_fails() -> None:
    token = jwt.encode(
        {"sub": "user-123", "exp": datetime.now(UTC) + timedelta(minutes=5)},
        key=None,
        algorithm="none",
    )

    result = JwtValidator(_config()).validate(token)

    assert result.success is False
    assert result.error is not None
    assert result.error.code == JwtErrorCode.UNSUPPORTED_ALGORITHM


def test_malformed_token_fails() -> None:
    result = JwtValidator(_config()).validate("not-a-jwt")

    assert result.success is False
    assert result.error is not None
    assert result.error.code == JwtErrorCode.MALFORMED_TOKEN


def test_missing_required_scope_fails() -> None:
    result = JwtValidator(_config(required_scopes=frozenset({"orders:delete"}))).validate(_token())

    assert result.success is False
    assert result.error is not None
    assert result.error.code == JwtErrorCode.INSUFFICIENT_SCOPE


def test_missing_required_role_fails() -> None:
    result = JwtValidator(_config(required_roles=frozenset({"super-admin"}))).validate(_token())

    assert result.success is False
    assert result.error is not None
    assert result.error.code == JwtErrorCode.INSUFFICIENT_ROLE


def test_custom_claim_validator_success_and_failure() -> None:
    success = CustomClaimValidator(
        name="tenant",
        validate=lambda claims: claims.get("tenant") == "tenant-a",
    )
    failure = CustomClaimValidator(
        name="tenant",
        validate=lambda claims: claims.get("tenant") == "tenant-b",
        error_message="tenant not allowed",
    )

    assert JwtValidator(_config(custom_claim_validators=(success,))).validate(_token()).success
    failed = JwtValidator(_config(custom_claim_validators=(failure,))).validate(_token())
    assert failed.error is not None
    assert failed.error.code == JwtErrorCode.INVALID_CLAIM
    assert failed.error.message == "tenant not allowed"


def test_jwks_key_rotation_and_kid_selection(monkeypatch: pytest.MonkeyPatch) -> None:
    jwk_one = dict(PUBLIC_JWK)
    jwk_one["kid"] = "key-1"
    jwk_two = dict(OTHER_PUBLIC_JWK)
    jwk_two["kid"] = "key-2"
    jwks_payloads = [
        {"keys": [jwk_one]},
        {"keys": [jwk_one, jwk_two]},
    ]
    calls = {"count": 0}

    class Response:
        def __enter__(self) -> Response:
            return self

        def __exit__(self, *args: object) -> None:
            return None

        def read(self) -> bytes:
            index = min(calls["count"], len(jwks_payloads) - 1)
            calls["count"] += 1
            return json.dumps(jwks_payloads[index]).encode("utf-8")

    monkeypatch.setattr("urllib.request.urlopen", lambda *args, **kwargs: Response())

    config = _config(
        static_public_key=None,
        jwks_url="https://issuer.example.com/.well-known/jwks.json",
        jwks_cache_ttl_seconds=300,
    )
    validator = JwtValidator(config)

    first = validator.validate(_token(kid="key-1"))
    second = validator.validate(_token(private_key=OTHER_PRIVATE_KEY, kid="key-2"))

    assert first.success is True
    assert second.success is True
    assert calls["count"] == 2


def test_clock_skew_allows_recent_expiration() -> None:
    token = _token(overrides={"exp": datetime.now(UTC) - timedelta(seconds=20)})

    result = JwtValidator(_config(clock_skew_seconds=30)).validate(token)

    assert result.success is True
