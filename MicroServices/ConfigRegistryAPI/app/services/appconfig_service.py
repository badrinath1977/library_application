from __future__ import annotations

import asyncio
from typing import Any

from enterprise_logging import get_logger

from app.core.settings import Settings
from app.models.request_models import (
    AppConfigInsertRequest,
    AppConfigSetActiveRequest,
    AppConfigUpdateRequest,
    AppConfigUpsertRequest,
)
from app.repositories.appconfig_repository import AppConfigRepository
from app.services.security import mask_config_row, protect_log_payload


class AppConfigService:
    def __init__(self, repository: AppConfigRepository, settings: Settings) -> None:
        self._repository = repository
        self._settings = settings
        self._logger = get_logger("services.appconfig")

    async def get_all(
        self,
        application_name: str,
        environment_name: str,
        only_active: bool,
        correlation_id: str,
    ) -> list[dict[str, Any]]:
        self._logger.info(
            "appconfig.get_all.request",
            protect_log_payload(
                {
                    "ApplicationName": application_name,
                    "EnvironmentName": environment_name,
                    "OnlyActive": only_active,
                },
                correlation_id,
            ),
        )
        rows = await asyncio.to_thread(
            self._repository.get_all,
            application_name,
            environment_name,
            only_active,
        )
        return [mask_config_row(row, self._settings) for row in rows]

    async def get_by_key(
        self,
        config_key: str,
        application_name: str,
        environment_name: str,
        correlation_id: str,
    ) -> dict[str, Any] | None:
        self._logger.info(
            "appconfig.get_by_key.request",
            protect_log_payload(
                {
                    "ConfigKey": config_key,
                    "ApplicationName": application_name,
                    "EnvironmentName": environment_name,
                },
                correlation_id,
            ),
        )
        row = await asyncio.to_thread(
            self._repository.get_by_key,
            config_key,
            application_name,
            environment_name,
        )
        return mask_config_row(row, self._settings) if row else None

    async def insert(
        self,
        request: AppConfigInsertRequest,
        correlation_id: str,
    ) -> dict[str, Any] | None:
        self._logger.info(
            "appconfig.insert.request",
            protect_log_payload(request.model_dump(by_alias=True), correlation_id),
        )
        row = await asyncio.to_thread(self._repository.insert, request)
        return mask_config_row(row, self._settings) if row else None

    async def update(
        self,
        config_id: int,
        request: AppConfigUpdateRequest,
        correlation_id: str,
    ) -> dict[str, Any] | None:
        self._logger.info(
            "appconfig.update.request",
            protect_log_payload(
                {"ConfigId": config_id, **request.model_dump(by_alias=True)},
                correlation_id,
            ),
        )
        row = await asyncio.to_thread(self._repository.update, config_id, request)
        return mask_config_row(row, self._settings) if row else None

    async def upsert(
        self,
        request: AppConfigUpsertRequest,
        correlation_id: str,
    ) -> dict[str, Any] | None:
        self._logger.info(
            "appconfig.upsert.request",
            protect_log_payload(request.model_dump(by_alias=True), correlation_id),
        )
        row = await asyncio.to_thread(self._repository.upsert, request)
        return mask_config_row(row, self._settings) if row else None

    async def set_active(
        self,
        config_id: int,
        request: AppConfigSetActiveRequest,
        correlation_id: str,
    ) -> dict[str, Any] | None:
        self._logger.info(
            "appconfig.set_active.request",
            protect_log_payload(
                {"ConfigId": config_id, **request.model_dump(by_alias=True)},
                correlation_id,
            ),
        )
        row = await asyncio.to_thread(self._repository.set_active, config_id, request)
        return mask_config_row(row, self._settings) if row else None
