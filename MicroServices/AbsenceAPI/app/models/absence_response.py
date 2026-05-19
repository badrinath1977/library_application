from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AbsenceRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    person_number: str | None = Field(default=None, alias="personNumber")
    person_id: int | None = Field(default=None, alias="personId")
    person_absence_entry_id: int | None = Field(default=None, alias="personAbsenceEntryId")
    absence_type: str | None = Field(default=None, alias="absenceType")
    absence_type_id: int | None = Field(default=None, alias="absenceTypeId")
    absence_pattern_cd: str | None = Field(default=None, alias="absencePatternCd")
    absence_status_cd: str | None = Field(default=None, alias="absenceStatusCd")
    approval_status_cd: str | None = Field(default=None, alias="approvalStatusCd")
    absence_disp_status: str | None = Field(default=None, alias="absenceDispStatus")
    start_date: date | None = Field(default=None, alias="startDate")
    end_date: date | None = Field(default=None, alias="endDate")
    start_date_time: datetime | None = Field(default=None, alias="startDateTime")
    end_date_time: datetime | None = Field(default=None, alias="endDateTime")
    submitted_date: date | None = Field(default=None, alias="submittedDate")
    creation_date: datetime | None = Field(default=None, alias="creationDate")
    last_update_date: datetime | None = Field(default=None, alias="lastUpdateDate")
    approval_datetime: datetime | None = Field(default=None, alias="approvalDatetime")
    duration: Decimal | None = None
    unit_of_measure: str | None = Field(default=None, alias="unitOfMeasure")
    formatted_duration: str | None = Field(default=None, alias="formattedDuration")
    comments: str | None = None
    employer: str | None = None
    legal_entity_id: int | None = Field(default=None, alias="legalEntityId")
    legislation_code: str | None = Field(default=None, alias="legislationCode")
    absence_entry_basic_flag: bool | int | None = Field(default=None, alias="absenceEntryBasicFlag")
    employee_shift_flag: bool | int | None = Field(default=None, alias="employeeShiftFlag")
    single_day_flag: bool | int | None = Field(default=None, alias="singleDayFlag")
    open_ended_flag: bool | int | None = Field(default=None, alias="openEndedFlag")
    absence_updatable_flag: bool | int | None = Field(default=None, alias="absenceUpdatableFlag")
    created_by: str | None = Field(default=None, alias="createdBy")
    last_updated_by: str | None = Field(default=None, alias="lastUpdatedBy")
    object_version_number: int | None = Field(default=None, alias="objectVersionNumber")


class Pagination(BaseModel):
    total_records: int = Field(default=0, alias="totalRecords")
    current_page: int = Field(default=1, alias="currentPage")
    page_size: int = Field(default=20, alias="pageSize")
    total_pages: int = Field(default=0, alias="totalPages")


class ExecutionInfo(BaseModel):
    procedure_name: str = Field(alias="procedureName")
    execution_time_ms: int = Field(alias="executionTimeMs")


class AbsenceSearchResponse(BaseModel):
    success: bool = True
    trace_id: str = Field(alias="traceId")
    data: list[AbsenceRecord]
    pagination: Pagination
    execution: ExecutionInfo


class ErrorResponse(BaseModel):
    success: bool = False
    trace_id: str = Field(alias="traceId")
    error: dict[str, str]


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str


def normalize_row_keys(row: dict[str, Any]) -> dict[str, Any]:
    return {key[:1].lower() + key[1:] if key else key: value for key, value in row.items()}

