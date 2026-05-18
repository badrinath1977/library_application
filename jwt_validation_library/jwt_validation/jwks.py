from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from threading import RLock
from typing import Any
from urllib.parse import urlparse

import jwt

from jwt_validation.config import JwtValidatorConfig
from jwt_validation.errors import JwtErrorCode, JwtValidationError


@dataclass(frozen=True, slots=True)
class _CachedJwks:
    fetched_at: float
    keys: dict[str, Any]


class JwksKeyResolver:
    def __init__(self, config: JwtValidatorConfig) -> None:
        self._config = config
        self._cache: _CachedJwks | None = None
        self._lock = RLock()

    def resolve_key(self, token_headers: dict[str, Any]) -> Any:
        if self._config.static_public_key is not None:
            return self._config.static_public_key

        kid = token_headers.get("kid")
        if not isinstance(kid, str) or not kid:
            raise JwtValidationError(
                JwtErrorCode.KEY_RESOLUTION_FAILED,
                "JWT header is missing kid required for JWKS key resolution",
            )

        keys = self._get_keys()
        try:
            return keys[kid]
        except KeyError as exc:
            with self._lock:
                self._cache = None
            keys = self._get_keys()
            if kid in keys:
                return keys[kid]
            raise JwtValidationError(
                JwtErrorCode.KEY_RESOLUTION_FAILED,
                f"No JWKS key found for kid: {kid}",
                details={"kid": kid},
            ) from exc

    def _get_keys(self) -> dict[str, Any]:
        now = time.monotonic()
        with self._lock:
            if (
                self._cache is not None
                and now - self._cache.fetched_at <= self._config.jwks_cache_ttl_seconds
            ):
                return self._cache.keys
            keys = self._fetch_keys()
            self._cache = _CachedJwks(fetched_at=now, keys=keys)
            return keys

    def _fetch_keys(self) -> dict[str, Any]:
        jwks_url = self._config.jwks_url
        if not jwks_url:
            raise JwtValidationError(
                JwtErrorCode.KEY_RESOLUTION_FAILED,
                "jwks_url is required for JWKS key resolution",
            )
        parsed = urlparse(jwks_url)
        if self._config.require_https_jwks and parsed.scheme != "https":
            raise JwtValidationError(
                JwtErrorCode.KEY_RESOLUTION_FAILED,
                "JWKS URL must use HTTPS",
                details={"jwks_url": jwks_url},
            )
        if parsed.scheme not in {"http", "https"}:
            raise JwtValidationError(
                JwtErrorCode.KEY_RESOLUTION_FAILED,
                "JWKS URL must use HTTP or HTTPS",
                details={"jwks_url": jwks_url},
            )

        try:
            request = urllib.request.Request(jwks_url, method="GET")  # noqa: S310
            with urllib.request.urlopen(  # noqa: S310
                request,
                timeout=self._config.jwks_request_timeout_seconds,
            ) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise JwtValidationError(
                JwtErrorCode.KEY_RESOLUTION_FAILED,
                "Failed to fetch or parse JWKS",
                details={"jwks_url": jwks_url},
            ) from exc

        jwks_keys = payload.get("keys") if isinstance(payload, dict) else None
        if not isinstance(jwks_keys, list):
            raise JwtValidationError(
                JwtErrorCode.KEY_RESOLUTION_FAILED,
                "JWKS response does not contain a keys array",
            )

        resolved: dict[str, Any] = {}
        for jwk in jwks_keys:
            if not isinstance(jwk, dict) or not isinstance(jwk.get("kid"), str):
                continue
            try:
                resolved[jwk["kid"]] = jwt.PyJWK.from_dict(jwk).key
            except jwt.PyJWTError:
                continue

        if not resolved:
            raise JwtValidationError(
                JwtErrorCode.KEY_RESOLUTION_FAILED,
                "JWKS response did not contain usable keys",
            )
        return resolved
