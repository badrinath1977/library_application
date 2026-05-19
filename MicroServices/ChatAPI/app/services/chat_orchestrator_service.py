from __future__ import annotations

from typing import Any

from app.models.request_models import ChatRequest
from app.models.response_models import ApiExecution, ChatResponse, ChatResponseBody
from app.services.api_execution_service import ApiExecutionService, DownstreamApiError
from app.services.audit_trace_service import AuditTraceService
from app.services.config_client_service import ConfigClientService
from app.services.conversation_memory_service import ConversationMemoryService
from app.services.intent_service import IntentService
from app.services.llm_response_service import LlmResponseService


WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


class ChatOrchestratorService:
    def __init__(
        self,
        *,
        config_client: ConfigClientService,
        memory_service: ConversationMemoryService,
        intent_service: IntentService,
        api_execution_service: ApiExecutionService,
        llm_response_service: LlmResponseService,
        audit_trace_service: AuditTraceService,
    ) -> None:
        self._config_client = config_client
        self._memory = memory_service
        self._intent = intent_service
        self._api = api_execution_service
        self._llm = llm_response_service
        self._audit = audit_trace_service

    async def handle_chat(self, request: ChatRequest, trace_id: str) -> ChatResponse:
        started = self._audit.mark()
        self._audit.event(trace_id, "request_received", request.model_dump(by_alias=True))
        self._memory.append_message(request.conversation_id, "user", request.message)
        runtime_config = await self._config_client.load_runtime_config(request.department, trace_id)
        memory_payload = self._memory.history_payload(request.conversation_id)
        decision = self._intent.select_intent(
            request.message,
            runtime_config.get("API_REGISTRY"),
            request.user_id,
            memory_payload.get("entities", {}),
        )
        self._audit.event(trace_id, "intent_selected", {"intent": decision.intent, "tags": decision.tags})

        if decision.api_config is None or decision.missing_fields:
            missing = decision.missing_fields or ["intent"]
            response = ChatResponseBody(
                type="clarification",
                message=self._clarification_message(missing),
                requiredFields=missing,
            )
            self._memory.append_message(request.conversation_id, "assistant", response.message)
            return ChatResponse(
                success=True,
                conversationId=request.conversation_id,
                traceId=trace_id,
                response=response,
                tags=["clarification"],
            )

        api_config = decision.api_config
        if self._requires_confirmation(api_config, runtime_config.get("AGENT_POLICY")):
            execution = ApiExecution(
                apiName=api_config.api_name,
                endpoint=api_config.endpoint,
                method=api_config.method.upper(),
                requestPayload=decision.parameters,
            )
            confirmation_id = self._memory.store_pending_action(
                request.conversation_id,
                {"api": api_config.model_dump(by_alias=True), "parameters": decision.parameters},
            )
            response = ChatResponseBody(
                type="confirmation_required",
                message="Please confirm before I execute this action.",
                confirmationId=confirmation_id,
            )
            return ChatResponse(
                success=True,
                conversationId=request.conversation_id,
                traceId=trace_id,
                response=response,
                apiExecution=execution,
                tags=[*decision.tags, "confirmation_required"],
            )

        try:
            execution, api_response = await self._api.execute(api_config, decision.parameters)
            self._audit.event(trace_id, "api_executed", execution.model_dump(by_alias=True))
        except DownstreamApiError as exc:
            await self._audit.error(trace_id, exc, data={"apiExecution": exc.api_execution.model_dump(by_alias=True)})
            return ChatResponse(
                success=False,
                conversationId=request.conversation_id,
                traceId=trace_id,
                error={
                    "code": "DOWNSTREAM_API_ERROR",
                    "message": "I could not retrieve details right now. Please try again later.",
                },
                apiExecution=exc.api_execution,
                tags=[*decision.tags, "error"],
            )

        answer, token_usage = await self._llm.generate(
            llm_config=runtime_config.get("LLM_CONFIG") or {},
            prompt_config=runtime_config.get("PROMPT_CONFIG") or {},
            user_message=request.message,
            downstream_response=api_response,
            memory=memory_payload,
            department=request.department,
        )
        response = ChatResponseBody(type="answer", message=answer)
        self._memory.append_message(request.conversation_id, "assistant", answer, {"traceId": trace_id})
        self._memory.update_context(
            request.conversation_id,
            entities=decision.parameters,
            api_execution=execution.model_dump(by_alias=True),
        )
        self._audit.event(
            trace_id,
            "completed",
            {
                "tokenUsage": token_usage.model_dump(by_alias=True),
                "executionTimeMs": self._audit.elapsed_ms(started),
                "tags": decision.tags,
            },
        )
        return ChatResponse(
            success=True,
            conversationId=request.conversation_id,
            traceId=trace_id,
            response=response,
            apiExecution=execution,
            tokenUsage=token_usage,
            tags=decision.tags,
        )

    async def handle_stream(self, request: ChatRequest, trace_id: str):
        yield {"event": "started", "conversationId": request.conversation_id, "traceId": trace_id}
        response = await self.handle_chat(request, trace_id)
        if response.api_execution:
            yield {"event": "api_execution", "apiExecution": response.api_execution.model_dump(by_alias=True)}
        if response.response and response.response.message:
            for chunk in self._llm.stream_chunks(response.response.message):
                yield {"event": "delta", "text": chunk}
            yield {
                "event": "completed",
                "response": response.response.model_dump(by_alias=True, exclude_none=True),
                "tokenUsage": response.token_usage.model_dump(by_alias=True) if response.token_usage else None,
                "tags": response.tags,
            }
        elif response.error:
            yield {"event": "error", "error": response.error, "tags": response.tags}

    @staticmethod
    def _requires_confirmation(api_config: Any, agent_policy: Any) -> bool:
        method_requires = api_config.method.upper() in WRITE_METHODS
        policy_allows_immediate = bool((agent_policy or {}).get("allowImmediateWrites", False))
        return bool(api_config.requires_confirmation or (method_requires and not policy_allows_immediate))

    @staticmethod
    def _clarification_message(missing_fields: list[str]) -> str:
        if missing_fields == ["intent"]:
            return "Which action would you like me to perform?"
        readable = ", ".join(missing_fields)
        return f"I need more information before I can continue. Please provide: {readable}."

