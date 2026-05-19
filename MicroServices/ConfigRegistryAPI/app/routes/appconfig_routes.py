from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request, status

from app.models.request_models import (
    AppConfigInsertRequest,
    AppConfigSetActiveRequest,
    AppConfigUpdateRequest,
    AppConfigUpsertRequest,
)
from app.models.response_models import ApiResponse
from app.services.appconfig_service import AppConfigService


router = APIRouter(prefix="/api/config", tags=["App Configuration"])


def _service(request: Request) -> AppConfigService:
    return request.app.state.appconfig_service


def _cid(request: Request) -> str:
    return getattr(request.state, "correlation_id", "")


@router.get("/all", response_model=ApiResponse)
async def get_all_configs(
    request: Request,
    ApplicationName: str = Query(..., min_length=1),
    EnvironmentName: str = Query(..., min_length=1),
    OnlyActive: bool = Query(True),
) -> ApiResponse:
    data = await _service(request).get_all(
        ApplicationName,
        EnvironmentName,
        OnlyActive,
        _cid(request),
    )
    return ApiResponse(correlationId=_cid(request), data=data)


@router.get("/by-key", response_model=ApiResponse)
async def get_config_by_key(
    request: Request,
    ConfigKey: str = Query(..., min_length=1),
    ApplicationName: str = Query(..., min_length=1),
    EnvironmentName: str = Query(..., min_length=1),
) -> ApiResponse:
    data = await _service(request).get_by_key(
        ConfigKey,
        ApplicationName,
        EnvironmentName,
        _cid(request),
    )
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Configuration not found")
    return ApiResponse(correlationId=_cid(request), data=data)


@router.post("", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
async def insert_config(request: Request, payload: AppConfigInsertRequest) -> ApiResponse:
    data = await _service(request).insert(payload, _cid(request))
    return ApiResponse(correlationId=_cid(request), data=data)


@router.put("/{config_id}", response_model=ApiResponse)
async def update_config(
    request: Request,
    config_id: int,
    payload: AppConfigUpdateRequest,
) -> ApiResponse:
    data = await _service(request).update(config_id, payload, _cid(request))
    return ApiResponse(correlationId=_cid(request), data=data)


@router.post("/upsert", response_model=ApiResponse)
async def upsert_config(request: Request, payload: AppConfigUpsertRequest) -> ApiResponse:
    data = await _service(request).upsert(payload, _cid(request))
    return ApiResponse(correlationId=_cid(request), data=data)


@router.patch("/{config_id}/active", response_model=ApiResponse)
async def set_config_active(
    request: Request,
    config_id: int,
    payload: AppConfigSetActiveRequest,
) -> ApiResponse:
    data = await _service(request).set_active(config_id, payload, _cid(request))
    return ApiResponse(correlationId=_cid(request), data=data)
