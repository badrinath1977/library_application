from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    department: str = Field(min_length=1)
    user_id: str = Field(alias="userId", min_length=1)
    conversation_id: str = Field(alias="conversationId", min_length=1)
    message: str = Field(min_length=1)


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    conversation_id: str = Field(alias="conversationId", min_length=1)
    trace_id: str = Field(alias="traceId", min_length=1)
    rating: int = Field(ge=1, le=5)
    comment: str | None = None
