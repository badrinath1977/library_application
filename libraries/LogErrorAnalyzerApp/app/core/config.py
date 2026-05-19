"""Runtime configuration."""

from __future__ import annotations

import os
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    app_name: str = "LogErrorAnalyzerApp"
    log_level: str = "INFO"
    supported_extensions: str = ".log,.txt"
    llm_provider: str = "mock"
    llm_timeout_seconds: int = 30
    llm_api_key_env: str = "LLM_API_KEY"
    ticket_provider: str = "mock"
    ticket_project_key: str = "LOG"
    max_file_size_mb: int = 25
    keyvault_config_path: str = "config/keyvault_library.config.json"
    app_error_db_log_config_path: str = "config/app_error_db_log.config.json"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def extension_set(self) -> set[str]:
        """Return normalized supported extensions."""

        return {
            extension.strip().lower()
            for extension in self.supported_extensions.split(",")
            if extension.strip()
        }

    @property
    def llm_api_key(self) -> str | None:
        """Return configured API key from the configured environment variable."""

        return os.getenv(self.llm_api_key_env)


@lru_cache
def get_settings() -> Settings:
    """Return cached settings."""

    return Settings()
