from __future__ import annotations

from fastapi import APIRouter, Request

from app.models.absence_request import AbsenceSearchRequest
from app.models.absence_response import AbsenceSearchResponse

router = APIRouter(prefix="/api/absence", tags=["Absence"])


@router.post("/search", response_model=AbsenceSearchResponse)
async def search_absence(request: Request, payload: AbsenceSearchRequest) -> AbsenceSearchResponse:
    return await request.app.state.absence_service.search(
        payload,
        getattr(request.state, "trace_id", ""),
    )

