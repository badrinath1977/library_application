from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class DepartmentMapping(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    departments: dict[str, str] = Field(default_factory=dict)


class ApiConfig(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    api_name: str = Field(alias="apiName")
    intent: str | None = None
    intent_keywords: list[str] = Field(default_factory=list, alias="intentKeywords")
    base_url: str = Field(alias="baseUrl")
    endpoint: str
    method: str = "GET"
    headers: dict[str, str] = Field(default_factory=dict)
    query_parameters: dict[str, Any] = Field(default_factory=dict, alias="queryParameters")
    path_parameters: dict[str, Any] = Field(default_factory=dict, alias="pathParameters")
    request_body_template: dict[str, Any] | None = Field(default=None, alias="requestBodyTemplate")
    required_parameters: list[str] = Field(default_factory=list, alias="requiredParameters")
    parameter_mapping: dict[str, Any] = Field(default_factory=dict, alias="parameterMapping")
    auth_config_key: str | None = Field(default=None, alias="authConfigKey")
    timeout: float | None = None
    retry_count: int = Field(default=0, alias="retryCount")
    requires_confirmation: bool = Field(default=False, alias="requiresConfirmation")
    response_mapping: dict[str, Any] = Field(default_factory=dict, alias="responseMapping")
    tags: list[str] = Field(default_factory=list)


class ApiRegistry(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    apis: list[ApiConfig] = Field(default_factory=list)
