from libraries.jwt_validation_library.jwt_validation import JwtValidator, JwtValidatorConfig

PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
...
-----END PUBLIC KEY-----"""

validator = JwtValidator(
    JwtValidatorConfig(
        static_public_key=PUBLIC_KEY,
        issuer="https://issuer.example.com",
        audience="api://orders",
        required_scopes=frozenset({"orders:read"}),
        return_claim="sub",
        allowed_algorithms=("RS256",),
    )
)

result = validator.validate("eyJhbGciOiJSUzI1NiIs...")
if result.success:
    print(f"Authenticated subject: {result.value.claim_value}")
else:
    print(f"Token rejected: {result.error.code} - {result.error.message}")
