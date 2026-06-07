import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any

import httpx

from app.core.config import ExternalApiSettings
from app.core.exceptions import AppException
from app.core.logger import get_app_logger


class ExternalApiService:
    def __init__(self, settings: ExternalApiSettings) -> None:
        self.settings = settings
        self.logger = get_app_logger(self.__class__.__name__)
        self._access_token: str | None = None
        self._access_token_expires_at: datetime | None = None
        self._token_lock = asyncio.Lock()

    async def send(self, payload: dict[str, Any]) -> Any:
        if not self.settings.enabled:
            raise AppException(
                "External API integration is disabled",
                status_code=503,
                error_code="EXTERNAL_API_DISABLED",
            )

        request_payload = dict(payload)
        headers = dict(self.settings.headers)

        if self.settings.oauth.enabled:
            token = await self._get_access_token()
            oauth_settings = self.settings.oauth
            prefix = oauth_settings.header_prefix.strip()
            headers[oauth_settings.header_name] = f"{prefix} {token}".strip()

        url = self._build_url()
        method = self.settings.method.upper()

        try:
            async with httpx.AsyncClient(
                timeout=self.settings.timeout_seconds,
                verify=self.settings.verify_ssl,
            ) as client:
                request_arguments: dict[str, Any] = {
                    "method": method,
                    "url": url,
                    "headers": headers,
                }
                if method in {"GET", "HEAD", "DELETE"}:
                    request_arguments["params"] = request_payload
                else:
                    request_arguments["json"] = request_payload

                response = await client.request(**request_arguments)
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise AppException(
                "External API request timed out",
                status_code=504,
                error_code="EXTERNAL_API_TIMEOUT",
            ) from exc
        except httpx.HTTPStatusError as exc:
            self.logger.error(
                "External API returned an error",
                extra={
                    "status_code": exc.response.status_code,
                    "details": exc.response.text,
                },
            )
            raise AppException(
                "External API returned an error",
                status_code=502,
                error_code="EXTERNAL_API_HTTP_ERROR",
                details={"external_status_code": exc.response.status_code},
            ) from exc
        except httpx.RequestError as exc:
            raise AppException(
                "External API is unavailable",
                status_code=502,
                error_code="EXTERNAL_API_UNAVAILABLE",
            ) from exc

        if not response.content:
            return None

        content_type = response.headers.get("content-type", "")
        if "application/json" in content_type.lower():
            return response.json()

        return {"content": response.text}

    async def _get_access_token(self) -> str:
        if self._token_is_valid():
            return self._access_token  # type: ignore[return-value]

        async with self._token_lock:
            if self._token_is_valid():
                return self._access_token  # type: ignore[return-value]

            return await self._request_access_token()

    async def _request_access_token(self) -> str:
        oauth_settings = self.settings.oauth
        missing_fields = [
            field
            for field, value in {
                "token_url": oauth_settings.token_url,
                "client_id": oauth_settings.client_id,
                "client_secret": oauth_settings.client_secret,
                "scope": oauth_settings.scope,
            }.items()
            if not value
        ]
        if missing_fields:
            raise AppException(
                "External API OAuth configuration is incomplete",
                status_code=500,
                error_code="EXTERNAL_API_OAUTH_CONFIG_ERROR",
                details={"missing_fields": missing_fields},
            )

        try:
            async with httpx.AsyncClient(
                timeout=self.settings.timeout_seconds,
                verify=self.settings.verify_ssl,
            ) as client:
                response = await client.post(
                    oauth_settings.token_url,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": oauth_settings.client_id,
                        "client_secret": oauth_settings.client_secret,
                        "scope": oauth_settings.scope,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                response.raise_for_status()
                token_response = response.json()
        except httpx.TimeoutException as exc:
            raise AppException(
                "OAuth token request timed out",
                status_code=504,
                error_code="EXTERNAL_API_TOKEN_TIMEOUT",
            ) from exc
        except (httpx.HTTPStatusError, httpx.RequestError, ValueError) as exc:
            raise AppException(
                "Unable to obtain external API access token",
                status_code=502,
                error_code="EXTERNAL_API_TOKEN_ERROR",
            ) from exc

        access_token = token_response.get("access_token")
        if not access_token:
            raise AppException(
                "Token endpoint did not return an access token",
                status_code=502,
                error_code="EXTERNAL_API_TOKEN_MISSING",
            )

        expires_in = int(token_response.get("expires_in", 300))
        self._access_token = access_token
        self._access_token_expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=max(expires_in - 30, 1)
        )
        return access_token

    def _token_is_valid(self) -> bool:
        return bool(
            self._access_token
            and self._access_token_expires_at
            and datetime.now(timezone.utc) < self._access_token_expires_at
        )

    def _build_url(self) -> str:
        return (
            f"{self.settings.base_url.rstrip('/')}/"
            f"{self.settings.endpoint.lstrip('/')}"
        )
