from __future__ import annotations

import time
from collections.abc import Iterable
from datetime import date
from decimal import Decimal
from typing import Any

from app.core.database import Database
from app.models.absence_request import AbsenceSearchRequest


class AbsenceRepositoryError(Exception):
    pass


class AbsenceRepository:
    PROCEDURE_NAME = "GenAI.sp_SearchEmployeeAbsence"
    COMMAND = (
        "{CALL GenAI.sp_SearchEmployeeAbsence "
        "(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, "
        "?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)}"
    )

    def __init__(self, database: Database) -> None:
        self._database = database

    def search(self, request: AbsenceSearchRequest) -> tuple[list[dict[str, Any]], int]:
        started = time.perf_counter()
        try:
            connection = self._database.connect()
            try:
                cursor = connection.cursor()
                cursor.execute(self.COMMAND, self._params(request))
                rows = self._rows_to_dicts(cursor)
                return rows, int((time.perf_counter() - started) * 1000)
            finally:
                connection.close()
        except Exception as exc:  # noqa: BLE001
            raise AbsenceRepositoryError("Absence search repository operation failed.") from exc

    @staticmethod
    def _params(request: AbsenceSearchRequest) -> tuple[Any, ...]:
        values = (
            request.person_number,
            request.person_id,
            request.person_absence_entry_id,
            request.absence_type,
            request.absence_type_id,
            request.absence_pattern_cd,
            request.absence_status_cd,
            request.approval_status_cd,
            request.absence_disp_status,
            request.start_date_from,
            request.start_date_to,
            request.end_date_from,
            request.end_date_to,
            request.submitted_date_from,
            request.submitted_date_to,
            request.creation_date_from,
            request.creation_date_to,
            request.last_update_date_from,
            request.last_update_date_to,
            request.approval_date_from,
            request.approval_date_to,
            request.duration_min,
            request.duration_max,
            request.unit_of_measure,
            request.comments_keyword,
            request.employer,
            request.legal_entity_id,
            request.legislation_code,
            request.absence_entry_basic_flag,
            request.employee_shift_flag,
            request.single_day_flag,
            request.open_ended_flag,
            request.absence_updatable_flag,
            request.created_by,
            request.last_updated_by,
            request.object_version_number,
            request.page_number,
            request.page_size,
            request.sort_column,
            request.sort_direction,
        )
        return tuple(AbsenceRepository._to_db_value(value) for value in values)

    @staticmethod
    def _to_db_value(value: Any) -> Any:
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, Decimal):
            return float(value)
        return value

    @staticmethod
    def _rows_to_dicts(cursor: Any) -> list[dict[str, Any]]:
        if cursor.description is None:
            return []
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row, strict=False)) for row in cursor.fetchall()]
