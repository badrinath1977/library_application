from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel


def _load_dotenv(path: Path) -> None:
    if not path.is_file():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def _bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _csv(name: str, default: tuple[str, ...] = ()) -> tuple[str, ...]:
    value = os.getenv(name)
    if not value:
        return default
    return tuple(item.strip() for item in value.split(",") if item.strip())


class Settings(BaseModel):
    app_name: str = "ChatAPI"
    app_version: str = "1.0.0"
    environment: str = "local"
    service_name: str = "chat-api"

    config_registry_base_url: str = "http://localhost:8000"
    config_registry_application_name: str = "ChatAPI"
    environment_name: str = "local"
    config_registry_timeout_seconds: float = 10.0
    config_registry_bearer_token: str | None = None

    auth_enabled: bool = True
    jwt_return_claim: str = "sub"
    jwt_jwks_url: str | None = None
    jwt_static_public_key: str | None = None
    jwt_issuer: str | None = None
    jwt_audience: str | None = None
    jwt_required_scopes: tuple[str, ...] = ()
    jwt_required_roles: tuple[str, ...] = ()
    jwt_allowed_algorithms: tuple[str, ...] = ("RS256",)
    jwt_clock_skew_seconds: int = 60
    jwt_require_https_jwks: bool = True

    log_level: str = "INFO"
    log_format: str = "json"
    log_file_path: str | None = "logs/chat-api.log"
    app_error_fallback_file: str = "logs/app-error-fallback.log"

    default_cache_ttl_seconds: int = 300
    http_timeout_seconds: float = 30.0
    max_recent_messages: int = 8
    pending_action_ttl_seconds: int = 900
    internal_debug_enabled: bool = False


@lru_cache
def get_settings() -> Settings:
    _load_dotenv(Path.cwd() / ".env")
    return Settings(
        app_name=os.getenv("APP_NAME", "ChatAPI"),
        app_version=os.getenv("APP_VERSION", "1.0.0"),
        environment=os.getenv("ENVIRONMENT", "local"),
        service_name=os.getenv("SERVICE_NAME", "chat-api"),
        config_registry_base_url=os.getenv("CONFIG_REGISTRY_BASE_URL", "http://localhost:8000"),
        config_registry_application_name=os.getenv("CONFIG_REGISTRY_APPLICATION_NAME", "ChatAPI"),
        environment_name=os.getenv("ENVIRONMENT_NAME", "local"),
        config_registry_timeout_seconds=float(os.getenv("CONFIG_REGISTRY_TIMEOUT_SECONDS", "10")),
        config_registry_bearer_token=os.getenv("CONFIG_REGISTRY_BEARER_TOKEN") or None,
        auth_enabled=_bool("AUTH_ENABLED", True),
        jwt_return_claim=os.getenv("JWT_RETURN_CLAIM", "sub"),
        jwt_jwks_url=os.getenv("JWT_JWKS_URL") or None,
        jwt_static_public_key=os.getenv("JWT_STATIC_PUBLIC_KEY") or None,
        jwt_issuer=os.getenv("JWT_ISSUER") or None,
        jwt_audience=os.getenv("JWT_AUDIENCE") or None,
        jwt_required_scopes=_csv("JWT_REQUIRED_SCOPES"),
        jwt_required_roles=_csv("JWT_REQUIRED_ROLES"),
        jwt_allowed_algorithms=_csv("JWT_ALLOWED_ALGORITHMS", ("RS256",)),
        jwt_clock_skew_seconds=int(os.getenv("JWT_CLOCK_SKEW_SECONDS", "60")),
        jwt_require_https_jwks=_bool("JWT_REQUIRE_HTTPS_JWKS", True),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        log_format=os.getenv("LOG_FORMAT", "json"),
        log_file_path=os.getenv("LOG_FILE_PATH", "logs/chat-api.log") or None,
        app_error_fallback_file=os.getenv("APP_ERROR_FALLBACK_FILE", "logs/app-error-fallback.log"),
        default_cache_ttl_seconds=int(os.getenv("DEFAULT_CACHE_TTL_SECONDS", "300")),
        http_timeout_seconds=float(os.getenv("HTTP_TIMEOUT_SECONDS", "30")),
        max_recent_messages=int(os.getenv("MAX_RECENT_MESSAGES", "8")),
        pending_action_ttl_seconds=int(os.getenv("PENDING_ACTION_TTL_SECONDS", "900")),
        internal_debug_enabled=_bool("INTERNAL_DEBUG_ENABLED", False),
    )

