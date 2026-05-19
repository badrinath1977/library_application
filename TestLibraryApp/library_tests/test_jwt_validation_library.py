"""Smoke test for jwt_validation installed from libraries-dist."""

from __future__ import annotations

import jwt
from jwt_validation import JwtValidator, JwtValidatorConfig


def run() -> str:
    signing_secret = "local-test-secret-with-at-least-32-bytes"
    token = jwt.encode(
        {
            "sub": "user-123",
            "iss": "test-issuer",
            "aud": "test-audience",
            "scope": "read write",
            "exp": 4102444800,
        },
        signing_secret,
        algorithm="HS256",
    )
    validator = JwtValidator(
        JwtValidatorConfig(
            static_public_key=signing_secret,
            issuer="test-issuer",
            audience="test-audience",
            required_scopes=frozenset({"read"}),
            return_claim="sub",
            allowed_algorithms=("HS256",),
        )
    )
    result = validator.validate(token)
    if not result.success or result.value is None:
        raise RuntimeError(f"JWT validation failed: {result.error}")
    return f"PASS jwt_validation: return_claim={result.value.claim_value}"


if __name__ == "__main__":
    print(run())
