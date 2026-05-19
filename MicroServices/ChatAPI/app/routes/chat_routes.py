from __future__ import annotations

import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.models.request_models import ChatRequest, FeedbackRequest
from app.models.response_models import ChatResponse

router = APIRouter(prefix="/api/chat", tags=["Chat"])


def _trace_id(request: Request) -> str:
    return getattr(request.state, "trace_id", "")


@router.post("", response_model=ChatResponse)
async def chat(request: Request, payload: ChatRequest) -> ChatResponse:
    return await request.app.state.chat_orchestrator.handle_chat(payload, _trace_id(request))


@router.post("/stream")
async def chat_stream(request: Request, payload: ChatRequest) -> StreamingResponse:
    async def events():
        async for event in request.app.state.chat_orchestrator.handle_stream(payload, _trace_id(request)):
            yield f"data: {json.dumps(event, default=str)}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")


@router.get("/history/{conversation_id}")
async def history(request: Request, conversation_id: str) -> dict:
    return request.app.state.memory_service.history_payload(conversation_id)


@router.post("/feedback")
async def feedback(request: Request, payload: FeedbackRequest) -> dict:
    request.app.state.audit_trace_service.event(
        _trace_id(request),
        "feedback_received",
        payload.model_dump(by_alias=True),
    )
    return {"success": True, "conversationId": payload.conversation_id, "traceId": _trace_id(request)}

