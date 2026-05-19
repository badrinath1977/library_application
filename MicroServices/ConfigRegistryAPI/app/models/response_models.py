from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AppConfigResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")

    config_id: int | None = Field(default=None, alias="ConfigId")
    application_name: str | None = Field(default=None, alias="ApplicationName")
    environment_name: str | None = Field(default=None, alias="EnvironmentName")
    config_key: str | None = Field(default=None, alias="ConfigKey")
    config_value: Any | None = Field(default=None, alias="ConfigValue")
    config_type: str | None = Field(default=None, alias="ConfigType")
    is_sensitive: bool | None = Field(default=None, alias="IsSensitive")
    is_active: bool | None = Field(default=None, alias="IsActive")
    description: str | None = Field(default=None, alias="Description")


class ApiResponse(BaseModel):
    success: bool = True
    correlation_id: str = Field(alias="correlationId")
    data: Any | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    correlation_id: str = Field(alias="correlationId")
    error: dict[str, Any]


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str

