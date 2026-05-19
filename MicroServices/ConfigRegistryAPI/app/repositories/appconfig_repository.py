from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from app.config.database import Database
from app.core.errors import DatabaseOperationError
from app.models.request_models import (
    AppConfigInsertRequest,
    AppConfigSetActiveRequest,
    AppConfigUpdateRequest,
    AppConfigUpsertRequest,
)


class AppConfigRepository:
    """Stored-procedure-only AppConfig access."""

    SP_GET_ALL = "{CALL GenAI.sp_AppConfig_GetAll (?, ?, ?)}"
    SP_GET_BY_KEY = "{CALL GenAI.sp_AppConfig_GetByKey (?, ?, ?)}"
    SP_INSERT = "{CALL GenAI.sp_AppConfig_Insert (?, ?, ?, ?, ?, ?, ?, ?, ?)}"
    SP_UPDATE = "{CALL GenAI.sp_AppConfig_Update (?, ?, ?, ?, ?, ?, ?)}"
    SP_UPSERT = "{CALL GenAI.sp_AppConfig_Upsert (?, ?, ?, ?, ?, ?, ?, ?, ?)}"
    SP_SET_ACTIVE = "{CALL GenAI.sp_AppConfig_SetActive (?, ?, ?)}"

    def __init__(self, database: Database) -> None:
        self._database = database

    def get_all(
        self,
        application_name: str,
        environment_name: str,
        only_active: bool,
    ) -> list[dict[str, Any]]:
        return self._fetch_all(
            self.SP_GET_ALL,
            (application_name, environment_name, only_active),
        )

    def get_by_key(
        self,
        config_key: str,
        application_name: str,
        environment_name: str,
    ) -> dict[str, Any] | None:
        rows = self._fetch_all(
            self.SP_GET_BY_KEY,
            (config_key, application_name, environment_name),
        )
        return rows[0] if rows else None

    def insert(self, request: AppConfigInsertRequest) -> dict[str, Any] | None:
        return self._execute_mutation(
            self.SP_INSERT,
            (
                request.application_name,
                request.environment_name,
                request.config_key,
                request.config_value,
                request.config_type,
                request.is_sensitive,
                request.is_active,
                request.description,
                request.created_by,
            ),
        )

    def update(self, config_id: int, request: AppConfigUpdateRequest) -> dict[str, Any] | None:
        return self._execute_mutation(
            self.SP_UPDATE,
            (
                config_id,
                request.config_value,
                request.config_type,
                request.is_sensitive,
                request.is_active,
                request.description,
                request.updated_by,
            ),
        )

    def upsert(self, request: AppConfigUpsertRequest) -> dict[str, Any] | None:
        actor = request.updated_by or request.created_by
        return self._execute_mutation(
            self.SP_UPSERT,
            (
                request.application_name,
                request.environment_name,
                request.config_key,
                request.config_value,
                request.config_type,
                request.is_sensitive,
                request.is_active,
                request.description,
                actor,
            ),
        )

    def set_active(self, config_id: int, request: AppConfigSetActiveRequest) -> dict[str, Any] | None:
        return self._execute_mutation(
            self.SP_SET_ACTIVE,
            (config_id, request.is_active, request.updated_by),
        )

    def _fetch_all(self, command: str, params: Iterable[Any]) -> list[dict[str, Any]]:
        try:
            connection = self._database.connect()
            try:
                cursor = connection.cursor()
                cursor.execute(command, tuple(params))
                return self._rows_to_dicts(cursor)
            finally:
                connection.close()
        except Exception as exc:  # noqa: BLE001
            raise DatabaseOperationError(str(exc)) from exc

    def _execute_mutation(self, command: str, params: Iterable[Any]) -> dict[str, Any] | None:
        try:
            connection = self._database.connect()
            try:
                cursor = connection.cursor()
                cursor.execute(command, tuple(params))
                rows = self._rows_to_dicts(cursor)
                connection.commit()
                return rows[0] if rows else None
            finally:
                connection.close()
        except Exception as exc:  # noqa: BLE001
            raise DatabaseOperationError(str(exc)) from exc

    @staticmethod
    def _rows_to_dicts(cursor: Any) -> list[dict[str, Any]]:
        if cursor.description is None:
            return []
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]
