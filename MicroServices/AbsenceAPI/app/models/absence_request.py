from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AbsenceSearchRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    person_number: str | None = Field(default=None, alias="personNumber")
    person_id: int | None = Field(default=None, alias="personId")
    person_absence_entry_id: int | None = Field(default=None, alias="personAbsenceEntryId")
    absence_type: str | None = Field(default=None, alias="absenceType")
    absence_type_id: int | None = Field(default=None, alias="absenceTypeId")
    absence_pattern_cd: str | None = Field(default=None, alias="absencePatternCd")
    absence_status_cd: str | None = Field(default=None, alias="absenceStatusCd")
    approval_status_cd: str | None = Field(default=None, alias="approvalStatusCd")
    absence_disp_status: str | None = Field(default=None, alias="absenceDispStatus")
    start_date_from: date | None = Field(default=None, alias="startDateFrom")
    start_date_to: date | None = Field(default=None, alias="startDateTo")
    end_date_from: date | None = Field(default=None, alias="endDateFrom")
    end_date_to: date | None = Field(default=None, alias="endDateTo")
    submitted_date_from: date | None = Field(default=None, alias="submittedDateFrom")
    submitted_date_to: date | None = Field(default=None, alias="submittedDateTo")
    creation_date_from: date | None = Field(default=None, alias="creationDateFrom")
    creation_date_to: date | None = Field(default=None, alias="creationDateTo")
    last_update_date_from: date | None = Field(default=None, alias="lastUpdateDateFrom")
    last_update_date_to: date | None = Field(default=None, alias="lastUpdateDateTo")
    approval_date_from: date | None = Field(default=None, alias="approvalDateFrom")
    approval_date_to: date | None = Field(default=None, alias="approvalDateTo")
    duration_min: Decimal | None = Field(default=None, alias="durationMin")
    duration_max: Decimal | None = Field(default=None, alias="durationMax")
    unit_of_measure: str | None = Field(default=None, alias="unitOfMeasure")
    comments_keyword: str | None = Field(default=None, alias="commentsKeyword")
    employer: str | None = None
    legal_entity_id: int | None = Field(default=None, alias="legalEntityId")
    legislation_code: str | None = Field(default=None, alias="legislationCode")
    absence_entry_basic_flag: bool | None = Field(default=None, alias="absenceEntryBasicFlag")
    employee_shift_flag: bool | None = Field(default=None, alias="employeeShiftFlag")
    single_day_flag: bool | None = Field(default=None, alias="singleDayFlag")
    open_ended_flag: bool | None = Field(default=None, alias="openEndedFlag")
    absence_updatable_flag: bool | None = Field(default=None, alias="absenceUpdatableFlag")
    created_by: str | None = Field(default=None, alias="createdBy")
    last_updated_by: str | None = Field(default=None, alias="lastUpdatedBy")
    object_version_number: int | None = Field(default=None, alias="objectVersionNumber")
    page_number: int = Field(default=1, alias="pageNumber", ge=1)
    page_size: int = Field(default=20, alias="pageSize", ge=1, le=200)
    sort_column: str | None = Field(default="startDate", alias="sortColumn")
    sort_direction: str | None = Field(default="DESC", alias="sortDirection")

    @field_validator("sort_direction")
    @classmethod
    def validate_sort_direction(cls, value: str | None) -> str | None:
        if value is None:
            return value
        normalized = value.upper()
        if normalized not in {"ASC", "DESC"}:
            raise ValueError("sortDirection must be ASC or DESC")
        return normalized

