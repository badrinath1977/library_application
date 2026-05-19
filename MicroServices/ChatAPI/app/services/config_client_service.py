from __future__ import annotations

import json
from typing import Any

import httpx
from enterprise_logging import get_logger

from app.core.cache_manager import TTLCache
from app.core.constants import CONFIG_KEYS
from app.core.settings import Settings
from app.services.pii_security_service import mask_for_log


class ConfigClientService:
    def __init__(self, client: httpx.AsyncClient, cache: TTLCache, settings: Settings) -> None:
        self._client = client
        self._cache = cache
        self._settings = settings
        self._logger = get_logger("services.config_client")

    async def get_config(
        self,
        config_key: str,
        application_name: str,
        environment_name: str,
        trace_id: str,
        ttl_seconds: int | None = None,
    ) -> Any:
        cache_key = f"config:{application_name}:{environment_name}:{config_key}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            self._logger.info("config.cache.hit", {"configKey": config_key, "traceId": trace_id})
            return cached

        self._logger.info("config.cache.miss", {"configKey": config_key, "traceId": trace_id})
        response = await self._client.get(
            "/api/config/by-key",
            params={
                "ConfigKey": config_key,
                "ApplicationName": application_name,
                "EnvironmentName": environment_name,
            },
            headers=self._headers(),
        )
        response.raise_for_status()
        payload = response.json()
        value = (payload.get("data") or {}).get("ConfigValue")
        parsed = self._parse_value(value)
        self._cache.set(cache_key, parsed, ttl_seconds)
        return parsed

    async def load_runtime_config(self, department: str, trace_id: str) -> dict[str, Any]:
        mapping = await self.get_config(
            CONFIG_KEYS["department_mapping"],
            self._settings.config_registry_application_name,
            self._settings.environment_name,
            trace_id,
        )
        application_name = self.resolve_application_name(department, mapping)
        keys = (
            CONFIG_KEYS["api_registry"],
            CONFIG_KEYS["llm"],
            CONFIG_KEYS["prompt"],
            CONFIG_KEYS["agent_policy"],
            CONFIG_KEYS["token_policy"],
            CONFIG_KEYS["cache_policy"],
            CONFIG_KEYS["auth_policy"],
        )
        loaded: dict[str, Any] = {
            "departmentMapping": mapping,
            "applicationName": application_name,
            "environmentName": self._settings.environment_name,
        }
        for key in keys:
            loaded[key] = await self.get_config(
                key,
                application_name,
                self._settings.environment_name,
                trace_id,
            )
        self._logger.info(
            "config.loaded",
            mask_for_log(
                {
                    "applicationName": application_name,
                    "environmentName": self._settings.environment_name,
                    "keys": list(keys),
                },
                trace_id,
            ),
        )
        return loaded

    @staticmethod
    def resolve_application_name(department: str, mapping: Any) -> str:
        data = mapping or {}
        departments = data.get("departments", data) if isinstance(data, dict) else {}
        application_name = departments.get(department) or departments.get(department.upper())
        if not application_name:
            raise ValueError(f"No application mapping configured for department '{department}'.")
        return str(application_name)

    @staticmethod
    def _parse_value(value: Any) -> Any:
        if not isinstance(value, str):
            return value
        stripped = value.strip()
        if not stripped:
            return stripped
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            return stripped

    def _headers(self) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self._settings.config_registry_bearer_token:
            headers["Authorization"] = f"Bearer {self._settings.config_registry_bearer_token}"
        return headers

