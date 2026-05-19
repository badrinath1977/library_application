from __future__ import annotations

import asyncio
from typing import Any

from app_error_db_log import AppErrorLogConfig, AppErrorLogger
from enterprise_logging import get_logger

from app.core.settings import Settings
from app.models.absence_request import AbsenceSearchRequest
from app.models.absence_response import (
    AbsenceRecord,
    AbsenceSearchResponse,
    ExecutionInfo,
    Pagination,
    normalize_row_keys,
)
from app.repositories.absence_repository import AbsenceRepository, AbsenceRepositoryError
from app.services.pii_security_service import mask_for_log


class AbsenceSearchFailed(Exception):
    pass


class AbsenceService:
    def __init__(self, repository: AbsenceRepository, settings: Settings) -> None:
        self._repository = repository
        self._settings = settings
        self._logger = get_logger("services.absence")
        self._error_logger = AppErrorLogger(
            AppErrorLogConfig(
                connection_string="",
                application_name=settings.app_name,
                fallback_file_path=settings.app_error_fallback_file,
                suppress_logger_errors=True,
            )
        )

    async def search(self, request: AbsenceSearchRequest, trace_id: str) -> AbsenceSearchResponse:
        normalized_request = self._apply_pagination_limits(request)
        self._logger.info(
            "absence.search.request",
            mask_for_log(normalized_request.model_dump(by_alias=True), trace_id),
        )
        try:
            rows, execution_time_ms = await asyncio.to_thread(self._repository.search, normalized_request)
        except AbsenceRepositoryError as exc:
            await self._error_logger.log_exception_async(
                exc,
                module_name="AbsenceAPI",
                correlation_id=trace_id,
                error_code="ABSENCE_SEARCH_FAILED",
                request_path="/api/absence/search",
                request_payload=mask_for_log(normalized_request.model_dump(by_alias=True), trace_id),
                additional_info={"procedureName": AbsenceRepository.PROCEDURE_NAME},
            )
            raise AbsenceSearchFailed("Unable to retrieve employee absence records.") from exc

        normalized_rows = [normalize_row_keys(row) for row in rows]
        pagination = self._pagination(normalized_rows, normalized_request)
        records = [
            AbsenceRecord.model_validate(self._without_pagination(row))
            for row in normalized_rows
        ]
        response = AbsenceSearchResponse(
            traceId=trace_id,
            data=records,
            pagination=pagination,
            execution=ExecutionInfo(
                procedureName=AbsenceRepository.PROCEDURE_NAME,
                executionTimeMs=execution_time_ms,
            ),
        )
        self._logger.info(
            "absence.search.completed",
            mask_for_log(
                {
                    "traceId": trace_id,
                    "recordCount": len(records),
                    "pagination": pagination.model_dump(by_alias=True),
                    "executionTimeMs": execution_time_ms,
                },
                trace_id,
            ),
        )
        return response

    def _apply_pagination_limits(self, request: AbsenceSearchRequest) -> AbsenceSearchRequest:
        data = request.model_dump()
        data["page_number"] = request.page_number or self._settings.default_page_number
        data["page_size"] = min(request.page_size or self._settings.default_page_size, self._settings.max_page_size)
        return AbsenceSearchRequest.model_validate(data)

    @staticmethod
    def _pagination(rows: list[dict[str, Any]], request: AbsenceSearchRequest) -> Pagination:
        first = rows[0] if rows else {}
        return Pagination(
            totalRecords=int(first.get("totalRecords") or 0),
            currentPage=int(first.get("currentPage") or request.page_number),
            pageSize=int(first.get("pageSize") or request.page_size),
            totalPages=int(first.get("totalPages") or 0),
        )

    @staticmethod
    def _without_pagination(row: dict[str, Any]) -> dict[str, Any]:
        clean = dict(row)
        for key in ("totalRecords", "currentPage", "pageSize", "totalPages"):
            clean.pop(key, None)
        return clean

