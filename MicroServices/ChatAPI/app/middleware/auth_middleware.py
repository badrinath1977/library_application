from __future__ import annotations

from jwt_validation import JwtValidator, JwtValidatorConfig
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.constants import SAFE_PUBLIC_PATHS
from app.core.settings import Settings


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: Settings) -> None:  # type: ignore[no-untyped-def]
        super().__init__(app)
        self._settings = settings
        self._validator = (
            self._build_validator(settings)
            if settings.auth_enabled and (settings.jwt_jwks_url or settings.jwt_static_public_key)
            else None
        )

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        if request.url.path in SAFE_PUBLIC_PATHS or request.url.path.startswith("/docs/") or not self._settings.auth_enabled:
            return await call_next(request)
        if self._validator is None:
            return self._error(request, 503, "authentication_not_configured", "JWT validation is enabled but no JWKS URL or static public key is configured.")
        auth = request.headers.get("Authorization", "")
        if not auth.lower().startswith("bearer "):
            return self._error(request, 401, "missing_bearer_token", "Bearer token is required.")
        result = self._validator.validate(auth.split(" ", 1)[1].strip())
        if not result.success or result.value is None:
            return self._error(
                request,
                401,
                str(result.error.code) if result.error else "invalid_token",
                result.error.message if result.error else "JWT validation failed.",
            )
        request.state.user_claim = result.value.claim_value
        request.state.jwt_claims = result.value.claims
        return await call_next(request)

    @staticmethod
    def _build_validator(settings: Settings) -> JwtValidator:
        return JwtValidator(
            JwtValidatorConfig(
                return_claim=settings.jwt_return_claim,
                jwks_url=settings.jwt_jwks_url,
                static_public_key=settings.jwt_static_public_key,
                issuer=settings.jwt_issuer,
                audience=settings.jwt_audience,
                required_scopes=frozenset(settings.jwt_required_scopes),
                required_roles=frozenset(settings.jwt_required_roles),
                allowed_algorithms=settings.jwt_allowed_algorithms,
                clock_skew_seconds=settings.jwt_clock_skew_seconds,
                require_https_jwks=settings.jwt_require_https_jwks,
            )
        )

    @staticmethod
    def _error(request: Request, status_code: int, code: str, message: str) -> JSONResponse:
        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "traceId": getattr(request.state, "trace_id", ""),
                "error": {"code": code, "message": message},
            },
            headers={"WWW-Authenticate": "Bearer"} if status_code == 401 else None,
        )

