# JWT Validation Library

Production-ready Python library for validating JWT access tokens with static public keys or JWKS-based key discovery.

## Security Assumptions

- Signature validation is always enabled.
- `alg=none` is rejected.
- Allowed algorithms must be explicitly configured.
- Issuer and audience validation are first-class configuration options.
- JWKS URLs must use HTTPS by default.
- Expiration is required and validated with configurable clock skew.

## Installation

```bash
pip install jwt-validation-library
```

For local development:

```bash
pip install -e .[dev]
```

## Basic Usage

```python
from jwt_validation import JwtValidator, JwtValidatorConfig

validator = JwtValidator(
    JwtValidatorConfig(
        jwks_url="https://issuer.example.com/.well-known/jwks.json",
        issuer="https://issuer.example.com",
        audience="api://orders",
        required_scopes=frozenset({"orders:read"}),
        return_claim="sub",
        allowed_algorithms=("RS256",),
        clock_skew_seconds=60,
    )
)

result = validator.validate(access_token)
if result.success:
    subject = result.value.claim_value
else:
    print(result.error.code, result.error.message)
```

## Configuration

`JwtValidatorConfig` supports:

- `jwks_url` or `static_public_key`
- `issuer`
- `audience`
- `subject`
- `required_scopes`
- `required_roles`
- `custom_claim_validators`
- `return_claim`
- `allowed_algorithms`
- `clock_skew_seconds`
- `jwks_cache_ttl_seconds`
- `jwks_request_timeout_seconds`
- `scope_claim_names`
- `role_claim_names`

Exactly one of `jwks_url` and `static_public_key` must be configured.

## JWKS Example

```python
validator = JwtValidator(
    JwtValidatorConfig(
        jwks_url="https://login.example.com/.well-known/jwks.json",
        issuer="https://login.example.com",
        audience="api://payments",
        return_claim="sub",
        allowed_algorithms=("RS256",),
        jwks_cache_ttl_seconds=300,
    )
)
```

The validator reads `kid` from the JWT header, fetches JWKS keys, caches them, and refreshes the cache when a token references an unknown `kid`.

## Static Public Key Example

```python
validator = JwtValidator(
    JwtValidatorConfig(
        static_public_key=PUBLIC_KEY_PEM,
        issuer="https://issuer.example.com",
        audience="api://orders",
        return_claim="email",
        allowed_algorithms=("RS256",),
    )
)
```

## Custom Claim Validation

```python
from jwt_validation import CustomClaimValidator

validator = JwtValidator(
    JwtValidatorConfig(
        jwks_url="https://issuer.example.com/.well-known/jwks.json",
        issuer="https://issuer.example.com",
        audience="api://orders",
        return_claim="tenant",
        custom_claim_validators=(
            CustomClaimValidator(
                name="tenant-active",
                validate=lambda claims: claims.get("tenant_status") == "active",
                error_message="tenant is not active",
            ),
        ),
    )
)
```

## Returning a Configured Claim

The validator returns the value of `return_claim` after successful validation:

```python
result = validator.validate(token)
if result.success:
    print(result.value.claim_value)
```

If the configured claim is missing, validation fails with `missing_claim`.

## Error Handling

```python
result = validator.validate(token)
if not result.success:
    match result.error.code:
        case JwtErrorCode.EXPIRED_TOKEN:
            print("Ask the client to refresh the token")
        case JwtErrorCode.INSUFFICIENT_SCOPE:
            print("Reject with 403")
        case _:
            print("Reject with 401")
```

For fail-fast code:

```python
try:
    success = validator.validate_or_raise(token)
except JwtValidationError as error:
    print(error.code, error.message)
```

## Structured Error Codes

- `expired_token`
- `invalid_signature`
- `missing_claim`
- `invalid_issuer`
- `invalid_audience`
- `insufficient_scope`
- `insufficient_role`
- `malformed_token`
- `unsupported_algorithm`
- `token_not_yet_valid`
- `invalid_claim`
- `key_resolution_failed`

## Public API

```python
validator = JwtValidator(config)
result = validator.validate(token)
success = validator.validate_or_raise(token)
```

`validate()` returns a `JwtValidationResult`:

```python
JwtValidationResult(
    success=True,
    value=JwtValidationSuccess(claim_value="user-123", claims={...}),
    error=None,
)
```

or:

```python
JwtValidationResult(
    success=False,
    value=None,
    error=JwtValidationError(code=JwtErrorCode.INVALID_SIGNATURE, message="..."),
)
```

## Security Notes

- Never disable signature validation.
- Never accept `alg=none`.
- Restrict `allowed_algorithms` to algorithms used by your identity provider.
- Validate both issuer and audience in production.
- Use HTTPS for JWKS URLs.
- Use short JWKS cache TTLs if your issuer rotates keys frequently.
- Do not use decoded claims for authorization until validation succeeds.
- Prefer scopes for permissions and roles for coarse-grained access control.

## Test

```bash
pytest
ruff check .
mypy jwt_validation
```
