"""API request models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class AnalyzeLogRequest(BaseModel):
    """Request for log analysis."""

    path: str = Field(..., min_length=1)
    recursive: bool = True
    call_llm: bool = False
    create_ticket: bool = False
    extensions: list[str] | None = None


class CreateTicketRequest(BaseModel):
    """Request to create a ticket for an analyzed error."""

    error_id: str = Field(..., min_length=1)

