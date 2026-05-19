from __future__ import annotations

from fastapi import APIRouter, Request

from app.models.absence_response import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health(request: Request) -> HealthResponse:
    settings = request.app.state.settings
    return HealthResponse(status="healthy", service=settings.service_name, version=settings.app_version, environment=settings.environment)


@router.get("/live", response_model=HealthResponse)
async def live(request: Request) -> HealthResponse:
    settings = request.app.state.settings
    return HealthResponse(status="live", service=settings.service_name, version=settings.app_version, environment=settings.environment)


@router.get("/ready", response_model=HealthResponse)
async def ready(request: Request) -> HealthResponse:
    settings = request.app.state.settings
    return HealthResponse(status="ready", service=settings.service_name, version=settings.app_version, environment=settings.environment)

