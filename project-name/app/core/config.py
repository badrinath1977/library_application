import json
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


CONFIG_PATH = Path(__file__).resolve().parents[2] / "config.json"


def _load_config_json() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}

    with CONFIG_PATH.open("r", encoding="utf-8") as config_file:
        return json.load(config_file)


def _env_or_config(env_name: str, config_value: Any) -> Any:
    env_value = os.getenv(env_name)
    if env_value is None:
        return config_value

    if isinstance(config_value, bool):
        return env_value.lower() in {"1", "true", "yes", "y"}

    if isinstance(config_value, list):
        return [item.strip() for item in env_value.split(",") if item.strip()]

    return env_value


def _to_list(value: Any) -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            return []
        if stripped.startswith("["):
            try:
                loaded = json.loads(stripped)
                return _to_list(loaded)
            except json.JSONDecodeError:
                pass
        return [item.strip() for item in stripped.split(",") if item.strip()]

    return [str(value)]


class CorsSettings(BaseModel):
    allow_origins: list[str] = Field(default_factory=lambda: ["*"])
    allow_credentials: bool = False
    allow_methods: list[str] = Field(default_factory=lambda: ["*"])
    allow_headers: list[str] = Field(default_factory=lambda: ["*"])


class KeyVaultSettings(BaseModel):
    url: str | None = None


class JwtSettings(BaseModel):
    required: bool = True
    audience: list[str] = Field(default_factory=list)
    issuer: list[str] = Field(default_factory=list)
    secret: str | None = None
    jwks_url: str | None = None
    algorithms: list[str] = Field(default_factory=lambda: ["HS256", "RS256"])


class ErrorDBSettings(BaseModel):
    enabled: bool = False
    path: str = "error_logs.db"


class DatabaseSettings(BaseModel):
    type: str = "sqlserver"
    server: str = r"localhost\SQLEXPRESS"
    database: str = "master"
    driver: str = "ODBC Driver 17 for SQL Server"
    trusted_connection: bool = True
    trust_server_certificate: bool = True
    connection_string: str | None = None


class ServerSettings(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True


class Settings(BaseModel):
    app_env: str = "local"
    service_name: str = "project-name"
    route_name: str = "sample"
    api_version: str = "1.0.0"
    api_prefix: str = "/api"
    docs_url: str | None = "docs"
    redoc_url: str | None = "redoc"
    openapi_url: str | None = "openapi.json"
    log_level: str = "INFO"
    server: ServerSettings = Field(default_factory=ServerSettings)
    cors: CorsSettings = Field(default_factory=CorsSettings)
    keyvault: KeyVaultSettings = Field(default_factory=KeyVaultSettings)
    jwt: JwtSettings = Field(default_factory=JwtSettings)
    error_db: ErrorDBSettings = Field(default_factory=ErrorDBSettings)
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)

    @property
    def is_local(self) -> bool:
        return self.app_env.lower() == "local"

    @property
    def keyvault_url(self) -> str | None:
        return self.keyvault.url

    @property
    def jwt_required(self) -> bool:
        return self.jwt.required

    @property
    def jwt_audience(self) -> list[str]:
        return self.jwt.audience

    @property
    def jwt_issuer(self) -> list[str]:
        return self.jwt.issuer

    @property
    def jwt_secret(self) -> str | None:
        return self.jwt.secret

    @property
    def jwt_jwks_url(self) -> str | None:
        return self.jwt.jwks_url

    @property
    def jwt_algorithms(self) -> str:
        return ",".join(self.jwt.algorithms)

    @property
    def error_db_enabled(self) -> bool:
        return self.error_db.enabled

    @property
    def error_db_path(self) -> str:
        return self.error_db.path

    @property
    def service_base_path(self) -> str:
        return f"{self.api_prefix.rstrip('/')}/{self.route_name.strip('/')}"

    @property
    def swagger_docs_path(self) -> str | None:
        return self._build_service_path(self.docs_url)

    @property
    def swagger_redoc_path(self) -> str | None:
        return self._build_service_path(self.redoc_url)

    @property
    def swagger_openapi_path(self) -> str | None:
        return self._build_service_path(self.openapi_url)

    def _build_service_path(self, value: str | None) -> str | None:
        if value is None:
            return None
        if value.startswith("/"):
            return value
        return f"{self.service_base_path}/{value.strip('/')}"

    def get_secret(self, name: str, default: Any = None) -> Any:
        env_value = os.getenv(name)
        fallback_value = env_value if env_value is not None else default

        if not self.keyvault_url:
            return fallback_value

        from app.core.keyvault import get_keyvault_provider

        return get_keyvault_provider(self.keyvault_url).get_secret(name, fallback_value)


def _build_settings() -> Settings:
    data = _load_config_json()

    data["app_env"] = _env_or_config("APP_ENV", data.get("app_env", "local"))
    data["service_name"] = _env_or_config("SERVICE_NAME", data.get("service_name", "project-name"))
    data["route_name"] = _env_or_config("ROUTE_NAME", data.get("route_name", "sample"))
    data["api_version"] = _env_or_config("API_VERSION", data.get("api_version", "1.0.0"))
    data["api_prefix"] = _env_or_config("API_PREFIX", data.get("api_prefix", "/api"))
    data["docs_url"] = _env_or_config("DOCS_URL", data.get("docs_url", "docs"))
    data["redoc_url"] = _env_or_config("REDOC_URL", data.get("redoc_url", "redoc"))
    data["openapi_url"] = _env_or_config("OPENAPI_URL", data.get("openapi_url", "openapi.json"))
    data["log_level"] = _env_or_config("LOG_LEVEL", data.get("log_level", "INFO"))

    cors = data.setdefault("cors", {})
    cors["allow_origins"] = _env_or_config("CORS_ALLOW_ORIGINS", cors.get("allow_origins", ["*"]))
    cors["allow_credentials"] = _env_or_config("CORS_ALLOW_CREDENTIALS", cors.get("allow_credentials", False))
    cors["allow_methods"] = _env_or_config("CORS_ALLOW_METHODS", cors.get("allow_methods", ["*"]))
    cors["allow_headers"] = _env_or_config("CORS_ALLOW_HEADERS", cors.get("allow_headers", ["*"]))

    server = data.setdefault("server", {})
    server["host"] = _env_or_config("HOST", server.get("host", "0.0.0.0"))
    server["port"] = int(_env_or_config("PORT", server.get("port", 8000)))
    server["reload"] = _env_or_config("RELOAD", server.get("reload", True))

    keyvault = data.setdefault("keyvault", {})
    keyvault["url"] = _env_or_config("KEYVAULT_URL", keyvault.get("url"))

    jwt = data.setdefault("jwt", {})
    jwt["required"] = _env_or_config("JWT_REQUIRED", jwt.get("required", True))
    jwt["audience"] = _to_list(_env_or_config("JWT_AUDIENCE", jwt.get("audience", [])))
    jwt["issuer"] = _to_list(_env_or_config("JWT_ISSUER", jwt.get("issuer", [])))
    jwt["secret"] = _env_or_config("JWT_SECRET", jwt.get("secret"))
    jwt["jwks_url"] = _env_or_config("JWT_JWKS_URL", jwt.get("jwks_url"))
    jwt["algorithms"] = _env_or_config("JWT_ALGORITHMS", jwt.get("algorithms", ["HS256", "RS256"]))

    error_db = data.setdefault("error_db", {})
    error_db["enabled"] = _env_or_config("ERROR_DB_ENABLED", error_db.get("enabled", False))
    error_db["path"] = _env_or_config("ERROR_DB_PATH", error_db.get("path", "error_logs.db"))

    database = data.setdefault("database", {})
    database["type"] = _env_or_config("DATABASE_TYPE", database.get("type", "sqlserver"))
    database["server"] = _env_or_config("DATABASE_SERVER", database.get("server", r"localhost\SQLEXPRESS"))
    database["database"] = _env_or_config("DATABASE_NAME", database.get("database", "master"))
    database["driver"] = _env_or_config("DATABASE_DRIVER", database.get("driver", "ODBC Driver 17 for SQL Server"))
    database["trusted_connection"] = _env_or_config(
        "DATABASE_TRUSTED_CONNECTION",
        database.get("trusted_connection", True),
    )
    database["trust_server_certificate"] = _env_or_config(
        "DATABASE_TRUST_SERVER_CERTIFICATE",
        database.get("trust_server_certificate", True),
    )
    database["connection_string"] = _env_or_config(
        "DATABASE_CONNECTION_STRING",
        database.get("connection_string"),
    )

    settings = Settings(**data)
    if not settings.is_local:
        settings.jwt.audience = _to_list(
            _env_or_config("JWT_AUDIENCE", settings.get_secret("JWT_AUDIENCE", settings.jwt.audience))
        )
        settings.jwt.issuer = _to_list(
            _env_or_config("JWT_ISSUER", settings.get_secret("JWT_ISSUER", settings.jwt.issuer))
        )
        settings.jwt.secret = settings.get_secret("JWT_SECRET", settings.jwt.secret)
        settings.jwt.jwks_url = settings.get_secret("JWT_JWKS_URL", settings.jwt.jwks_url)

    return settings


@lru_cache
def get_settings() -> Settings:
    return _build_settings()
