from app.models.request_models import ChatRequest
from app.models.response_models import ChatResponse, ChatResponseBody


def test_chat_request_aliases() -> None:
    request = ChatRequest.model_validate(
        {
            "department": "HR",
            "userId": "41556",
            "conversationId": "conv-001",
            "message": "Show me sick leaves",
        }
    )
    assert request.user_id == "41556"
    assert request.conversation_id == "conv-001"


def test_chat_response_aliases() -> None:
    response = ChatResponse(
        success=True,
        conversationId="conv-001",
        traceId="trace-001",
        response=ChatResponseBody(type="answer", message="done"),
        tags=["test"],
    )
    payload = response.model_dump(by_alias=True)
    assert payload["conversationId"] == "conv-001"
    assert payload["traceId"] == "trace-001"

