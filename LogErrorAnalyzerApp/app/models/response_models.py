"""API response models."""

from __future__ import annotations

from pydantic import BaseModel


class TicketResponse(BaseModel):
    """Ticket creation result."""

    created: bool
    ticket_id: str | None = None
    error: str | None = None


class ErrorAnalysisResponse(BaseModel):
    """Structured error analysis result."""

    id: str
    error_message: str | None = None
    exception_type: str | None = None
    stacktrace: str
    method_name: str | None = None
    file_name: str | None = None
    line_number: int | None = None
    class_name: str | None = None
    module_name: str | None = None
    timestamp: str | None = None
    log_level: str | None = None
    occurrence_count: int
    most_recent_occurrence: str | None = None
    root_cause_guess: str | None = None
    is_application_file: bool | None = None
    raw_error_block: str
    llm_solution: str | None = None
    ticket: TicketResponse | None = None


class AnalyzeSummary(BaseModel):
    """Analysis summary counts."""

    files_scanned: int
    errors_found: int
    unique_errors: int


class AnalyzeLogResponse(BaseModel):
    """Response from log analysis."""

    status: str
    summary: AnalyzeSummary
    errors: list[ErrorAnalysisResponse]


class HealthResponse(BaseModel):
    """Health response."""

    status: str
    service: str
    keyvault: dict[str, object] | None = None
