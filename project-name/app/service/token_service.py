from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

from app.core.config import Settings
from app.core.exceptions import AppException
from app.models.request_models import TestTokenRequest


class TokenService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def create_test_token(self, request: TestTokenRequest) -> dict:
        jwt_settings = self.settings.jwt

        if not self.settings.is_local or not jwt_settings.test_token_enabled:
            raise AppException(
                "Test token creation is disabled",
                status_code=404,
                error_code="TEST_TOKEN_DISABLED",
            )

        if not jwt_settings.secret:
            raise AppException(
                "JWT secret is not configured",
                status_code=500,
                error_code="JWT_CONFIG_ERROR",
            )

        audience = request.audience or self._default_audience()
        if audience not in jwt_settings.audience:
            raise AppException(
                "Requested audience is not allowed",
                status_code=400,
                error_code="INVALID_TEST_TOKEN_AUDIENCE",
                details={"allowed_audiences": jwt_settings.audience},
            )
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(seconds=jwt_settings.test_token_expiry_seconds)

        claims = {
            "sub": request.email,
            "email": request.email,
            "aud": audience,
            "iss": self._default_issuer(),
            "iat": now,
            "nbf": now,
            "exp": expires_at,
            "jti": str(uuid4()),
        }

        token = jwt.encode(claims, jwt_settings.secret, algorithm="HS256")
        return {
            "access_token": token,
            "token_type": "Bearer",
            "expires_at": expires_at.isoformat(),
            "claims": {
                "email": request.email,
                "aud": audience,
                "iss": claims["iss"],
            },
        }

    def _default_audience(self) -> str:
        if not self.settings.jwt.audience:
            raise AppException(
                "JWT audience is not configured",
                status_code=500,
                error_code="JWT_CONFIG_ERROR",
            )
        return self.settings.jwt.audience[0]

    def _default_issuer(self) -> str:
        if not self.settings.jwt.issuer:
            raise AppException(
                "JWT issuer is not configured",
                status_code=500,
                error_code="JWT_CONFIG_ERROR",
            )
        return self.settings.jwt.issuer[0]
