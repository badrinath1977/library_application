"""API routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.core.config import get_settings
from app.core.exceptions import LogAnalyzerError
from app.core.library_integrations import get_keyvault_status, log_exception_to_db
from app.models.request_models import AnalyzeLogRequest, CreateTicketRequest
from app.models.response_models import (
    AnalyzeLogResponse,
    AnalyzeSummary,
    ErrorAnalysisResponse,
    HealthResponse,
    TicketResponse,
)
from app.services.error_analyzer import ErrorAnalyzer
from app.services.llm_service import LLMService
from app.services.log_parser import ParsedError, LogParser
from app.services.log_reader import LogReader
from app.services.ticket_service import TicketService
from app.utils.file_utils import discover_log_files

router = APIRouter()
logger = logging.getLogger(__name__)
ERROR_STORE: dict[str, ErrorAnalysisResponse] = {}


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Health endpoint."""

    return HealthResponse(
        status="ok",
        service=get_settings().app_name,
        keyvault=get_keyvault_status(),
    )


@router.post("/analyze-log", response_model=AnalyzeLogResponse)
async def analyze_log(request: AnalyzeLogRequest) -> AnalyzeLogResponse:
    """Analyze a log file or folder."""

    settings = get_settings()
    extensions = {
        extension.lower() if extension.startswith(".") else f".{extension.lower()}"
        for extension in (request.extensions or list(settings.extension_set))
    }
    try:
        files = discover_log_files(request.path, extensions, request.recursive)
        reader = LogReader(settings.max_file_size_mb)
        parser = LogParser()
        parsed_errors: list[ParsedError] = []
        files_scanned = 0
        for file_path in files:
            try:
                content = reader.read_file(file_path)
                files_scanned += 1
                if content.strip():
                    parsed_errors.extend(parser.parse(content, file_path))
            except LogAnalyzerError:
                logger.exception("Skipping unreadable log file: %s", file_path)
                log_exception_to_db(
                    LogAnalyzerError(f"Skipping unreadable log file: {file_path}"),
                    module_name="LogReader",
                    request_path="/analyze-log",
                    additional_info={"file_path": str(file_path)},
                )

        errors = ErrorAnalyzer().analyze(parsed_errors)
        llm_service = LLMService(settings)
        ticket_service = TicketService(settings)
        for error in errors:
            if request.call_llm:
                try:
                    error.llm_solution = await llm_service.suggest_solution(error)
                except LogAnalyzerError as exc:
                    error.llm_solution = f"LLM solution unavailable: {exc}"
            if request.create_ticket:
                error.ticket = await ticket_service.create_ticket(error)
            ERROR_STORE[error.id] = error

        return AnalyzeLogResponse(
            status="success",
            summary=AnalyzeSummary(
                files_scanned=files_scanned,
                errors_found=len(parsed_errors),
                unique_errors=len(errors),
            ),
            errors=errors,
        )
    except LogAnalyzerError as exc:
        logger.exception("Log analysis failed")
        log_exception_to_db(
            exc,
            module_name="AnalyzeLogRoute",
            request_path="/analyze-log",
            additional_info={"input_path": request.path},
        )
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected log analysis failure")
        log_exception_to_db(
            exc,
            module_name="AnalyzeLogRoute",
            request_path="/analyze-log",
            additional_info={"input_path": request.path},
        )
        raise HTTPException(status_code=500, detail="Internal analysis error") from exc


@router.get("/errors/{error_id}", response_model=ErrorAnalysisResponse)
def get_error(error_id: str) -> ErrorAnalysisResponse:
    """Return previously analyzed error by ID."""

    error = ERROR_STORE.get(error_id)
    if error is None:
        raise HTTPException(status_code=404, detail="Error not found")
    return error


@router.post("/create-ticket", response_model=TicketResponse)
async def create_ticket(request: CreateTicketRequest) -> TicketResponse:
    """Create a ticket for a previously analyzed error."""

    error = ERROR_STORE.get(request.error_id)
    if error is None:
        exc = LogAnalyzerError(f"Error not found: {request.error_id}")
        log_exception_to_db(
            exc,
            module_name="CreateTicketRoute",
            request_path="/create-ticket",
            additional_info={"error_id": request.error_id},
        )
        raise HTTPException(status_code=404, detail="Error not found")
    ticket = await TicketService(get_settings()).create_ticket(error)
    error.ticket = ticket
    return ticket
