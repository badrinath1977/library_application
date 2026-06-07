from fastapi import Request

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError


PUBLIC_PATHS = {"/docs", "/openapi.json", "/redoc"}
PUBLIC_PATH_CONTAINS = ("/health",)
PUBLIC_PATH_SUFFIXES = ("/docs", "/openapi.json", "/redoc")
PUBLIC_TEST_PATH_SUFFIXES = ("/auth/test-token",)


async def jwt_auth_middleware(request: Request, call_next):
    if (
        request.url.path in PUBLIC_PATHS
        or any(path_part in request.url.path for path_part in PUBLIC_PATH_CONTAINS)
        or request.url.path.endswith(PUBLIC_PATH_SUFFIXES)
        or request.url.path.endswith(PUBLIC_TEST_PATH_SUFFIXES)
    ):
        request.state.user = None
        return await call_next(request)

    settings = get_settings()
    if not settings.jwt_required and settings.is_local:
        request.state.user = {"sub": "local-dev"}
        return await call_next(request)

    token = _extract_bearer_token(request)
    request.state.user = _validate_token(token, settings)
    return await call_next(request)


def _extract_bearer_token(request: Request) -> str:
    authorization = request.headers.get("Authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise AuthenticationError("Missing bearer token")
    return token


def _validate_token(token: str, settings):
    try:
        import jwt
    except ImportError as exc:
        raise AuthenticationError("PyJWT is not installed") from exc

    algorithms = [algorithm.strip() for algorithm in settings.jwt_algorithms.split(",") if algorithm.strip()]
    decode_options = {
        "verify_aud": bool(settings.jwt_audience),
        "verify_iss": False,
    }

    try:
        if settings.jwt_jwks_url:
            jwks_client = jwt.PyJWKClient(settings.jwt_jwks_url)
            signing_key = jwks_client.get_signing_key_from_jwt(token)
            return jwt.decode(
                token,
                signing_key.key,
                algorithms=algorithms,
                audience=settings.jwt_audience,
                options=decode_options,
            )
            _validate_issuer(claims, settings.jwt_issuer)
            return claims

        if not settings.jwt_secret:
            raise AuthenticationError("JWT_SECRET or JWT_JWKS_URL is required")

        claims = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=algorithms,
            audience=settings.jwt_audience,
            options=decode_options,
        )
        _validate_issuer(claims, settings.jwt_issuer)
        return claims
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationError("Token has expired") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthenticationError("Invalid token") from exc


def _validate_issuer(claims: dict, allowed_issuers: list[str]) -> None:
    if not allowed_issuers:
        return

    issuer = claims.get("iss")
    if issuer not in allowed_issuers:
        raise AuthenticationError("Invalid token issuer")
