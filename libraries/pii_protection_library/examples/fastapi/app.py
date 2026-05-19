from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from libraries.pii_protection_library.pii_protection import PiiProtectionService, PiiRequestContext
from libraries.pii_protection_library.pii_protection.config_loader import PiiConfigLoader

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "pii-config.json"

app = FastAPI(title="PII Protection Sample")
service = PiiProtectionService()
config = PiiConfigLoader().load(CONFIG_PATH)


class ProtectRequest(BaseModel):
    payload: dict[str, Any]
    context: dict[str, Any]


class RestoreRequest(BaseModel):
    payload: str | dict[str, Any]
    correlation_id: str = Field(alias="correlationId")
    context: dict[str, Any]


@app.post("/pii/protect")
def protect_endpoint(request: ProtectRequest) -> dict[str, Any]:
    result = service.protect(
        request.payload,
        config,
        PiiRequestContext.model_validate(request.context),
    )
    return result.model_dump(by_alias=True)


@app.post("/pii/restore")
def restore_endpoint(request: RestoreRequest) -> dict[str, Any]:
    result = service.restore(
        request.payload,
        request.correlation_id,
        config,
        PiiRequestContext.model_validate(request.context),
    )
    return result.model_dump(by_alias=True)
