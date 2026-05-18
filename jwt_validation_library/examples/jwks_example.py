from jwt_validation import CustomClaimValidator, JwtValidator, JwtValidatorConfig

validator = JwtValidator(
    JwtValidatorConfig(
        jwks_url="https://issuer.example.com/.well-known/jwks.json",
        issuer="https://issuer.example.com",
        audience="api://orders",
        required_roles=frozenset({"admin"}),
        return_claim="tenant",
        allowed_algorithms=("RS256",),
        custom_claim_validators=(
            CustomClaimValidator(
                name="tenant-active",
                validate=lambda claims: claims.get("tenant_status") == "active",
            ),
        ),
    )
)

validated = validator.validate_or_raise("eyJhbGciOiJSUzI1NiIs...")
print(validated.claim_value)
