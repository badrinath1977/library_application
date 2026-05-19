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
    app_name: str = "AbsenceAPI"
    app_version: str = "1.0.0"
    environment: str = "local"
    service_name: str = "absence-api"

    sql_server_connection_string: str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost\\SQLEXPRESS;"
        "DATABASE=genai_db;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )
    db_timeout_seconds: int = 30

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
    log_file_path: str | None = "logs/absence-api.log"
    app_error_fallback_file: str = "logs/app-error-fallback.log"

    default_page_number: int = 1
    default_page_size: int = 20
    max_page_size: int = 200


@lru_cache
def get_settings() -> Settings:
    _load_dotenv(Path.cwd() / ".env")
    return Settings(
        app_name=os.getenv("APP_NAME", "AbsenceAPI"),
        app_version=os.getenv("APP_VERSION", "1.0.0"),
        environment=os.getenv("ENVIRONMENT", "local"),
        service_name=os.getenv("SERVICE_NAME", "absence-api"),
        sql_server_connection_string=os.getenv(
            "SQL_SERVER_CONNECTION_STRING",
            Settings().sql_server_connection_string,
        ),
        db_timeout_seconds=int(os.getenv("DB_TIMEOUT_SECONDS", "30")),
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
        log_file_path=os.getenv("LOG_FILE_PATH", "logs/absence-api.log") or None,
        app_error_fallback_file=os.getenv("APP_ERROR_FALLBACK_FILE", "logs/app-error-fallback.log"),
        default_page_number=int(os.getenv("DEFAULT_PAGE_NUMBER", "1")),
        default_page_size=int(os.getenv("DEFAULT_PAGE_SIZE", "20")),
        max_page_size=int(os.getenv("MAX_PAGE_SIZE", "200")),
    )

