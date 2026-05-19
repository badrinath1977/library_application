from __future__ import annotations

from enterprise_logging import get_logger
from jwt_validation import JwtValidator, JwtValidatorConfig
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.settings import Settings


PUBLIC_PATHS = {"/health", "/ready", "/live", "/docs", "/redoc", "/openapi.json"}


class AuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, settings: Settings) -> None:  # type: ignore[no-untyped-def]
        super().__init__(app)
        self._settings = settings
        self._logger = get_logger("middleware.auth")
        self._validator = (
            self._build_validator(settings)
            if settings.auth_enabled
            and (settings.jwt_jwks_url or settings.jwt_static_public_key)
            else None
        )

    async def dispatch(self, request: Request, call_next) -> Response:  # type: ignore[no-untyped-def]
        if self._is_public_path(request.url.path) or not self._settings.auth_enabled:
            return await call_next(request)

        if self._validator is None:
            return JSONResponse(
                status_code=503,
                content={
                    "success": False,
                    "correlationId": getattr(request.state, "correlation_id", ""),
                    "error": {
                        "code": "authentication_not_configured",
                        "message": "JWT validation is enabled but no JWKS URL or static public key is configured.",
                    },
                },
            )

        header = request.headers.get("Authorization", "")
        if not header.lower().startswith("bearer "):
            return self._unauthorized(request, "missing_bearer_token", "Bearer token is required")

        token = header.split(" ", 1)[1].strip()
        result = self._validator.validate(token)
        if not result.success or result.value is None:
            error_code = str(result.error.code) if result.error else "invalid_token"
            message = result.error.message if result.error else "JWT validation failed"
            self._logger.warn(
                "auth.jwt.denied",
                {
                    "errorCode": error_code,
                    "path": request.url.path,
                    "correlationId": getattr(request.state, "correlation_id", None),
                },
            )
            return self._unauthorized(request, error_code, message)

        request.state.user_claim = result.value.claim_value
        request.state.jwt_claims = result.value.claims
        return await call_next(request)

    @staticmethod
    def _is_public_path(path: str) -> bool:
        return path in PUBLIC_PATHS or path.startswith("/docs/") or path.startswith("/static/")

    @staticmethod
    def _build_validator(settings: Settings) -> JwtValidator:
        config = JwtValidatorConfig(
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
        return JwtValidator(config)

    @staticmethod
    def _unauthorized(request: Request, code: str, message: str) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "correlationId": getattr(request.state, "correlation_id", ""),
                "error": {"code": code, "message": message},
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
