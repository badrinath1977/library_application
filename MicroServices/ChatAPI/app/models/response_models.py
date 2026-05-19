from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


ResponseType = Literal["answer", "clarification", "confirmation_required", "action_completed", "error"]


class ChatResponseBody(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: ResponseType
    message: str
    data: Any | None = None
    required_fields: list[str] | None = Field(default=None, alias="requiredFields")
    confirmation_id: str | None = Field(default=None, alias="confirmationId")


class ApiExecution(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    api_name: str = Field(alias="apiName")
    endpoint: str
    method: str
    request_payload: dict[str, Any] | None = Field(default=None, alias="requestPayload")
    status_code: int | None = Field(default=None, alias="statusCode")
    execution_time_ms: int | None = Field(default=None, alias="executionTimeMs")


class TokenUsageResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    input_tokens: int = Field(alias="inputTokens")
    output_tokens: int = Field(alias="outputTokens")
    total_tokens: int = Field(alias="totalTokens")
    provider: str
    model: str


class ChatResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    success: bool
    conversation_id: str = Field(alias="conversationId")
    trace_id: str = Field(alias="traceId")
    response: ChatResponseBody | None = None
    error: dict[str, str] | None = None
    api_execution: ApiExecution | None = Field(default=None, alias="apiExecution")
    token_usage: TokenUsageResponse | None = Field(default=None, alias="tokenUsage")
    tags: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    environment: str
