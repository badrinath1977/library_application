from __future__ import annotations

import json
from typing import Any

from enterprise_logging import get_logger

try:
    from llm_platform_library import LLMClient, LLMMessage
except Exception:  # noqa: BLE001
    from libraries.llm_platform_library.llm_platform_library import LLMClient, LLMMessage

from app.models.response_models import TokenUsageResponse


class LlmResponseService:
    def __init__(self) -> None:
        self._logger = get_logger("services.llm")

    async def generate(
        self,
        *,
        llm_config: dict[str, Any],
        prompt_config: dict[str, Any],
        user_message: str,
        downstream_response: Any,
        memory: dict[str, Any],
        department: str,
    ) -> tuple[str, TokenUsageResponse]:
        messages = self._build_messages(prompt_config, user_message, downstream_response, memory)
        client = LLMClient.from_dict(self._normalize_llm_config(llm_config))
        response = client.generate_response_with_messages(messages)
        content = response.content
        if response.provider.lower() == "mock":
            content = self._mock_grounded_answer(downstream_response)
        return content, TokenUsageResponse(
            inputTokens=response.usage.prompt_tokens,
            outputTokens=response.usage.completion_tokens,
            totalTokens=response.usage.total_tokens,
            provider=response.provider,
            model=response.model,
        )

    def stream_chunks(self, text: str) -> list[str]:
        words = text.split(" ")
        chunks: list[str] = []
        current = ""
        for word in words:
            current = f"{current}{word} "
            if len(current) >= 24:
                chunks.append(current)
                current = ""
        if current:
            chunks.append(current)
        return chunks

    @staticmethod
    def _build_messages(
        prompt_config: dict[str, Any],
        user_message: str,
        downstream_response: Any,
        memory: dict[str, Any],
    ) -> list[LLMMessage]:
        system_prompt = prompt_config.get("systemPrompt") or (
            "Use only verified downstream API response. Do not hallucinate. "
            "Do not invent dates, statuses, balances, names, or IDs. "
            "If data is missing, say it is unavailable. Do not expose chain-of-thought. "
            "Provide a concise professional response."
        )
        user_prompt = {
            "userMessage": user_message,
            "conversationSummary": memory.get("summary"),
            "recentMessages": memory.get("recentMessages", []),
            "verifiedApiResponse": downstream_response,
        }
        return [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=json.dumps(user_prompt, default=str)),
        ]

    @staticmethod
    def _normalize_llm_config(config: dict[str, Any]) -> dict[str, Any]:
        return {
            "Provider": config.get("Provider") or config.get("provider") or "mock",
            "DefaultModel": config.get("DefaultModel") or config.get("model") or config.get("defaultModel") or "mock-model",
            "LogLocation": config.get("LogLocation") or config.get("logLocation") or "logs",
            "PromptFolder": config.get("PromptFolder") or config.get("promptFolder") or "prompts",
            "Departments": config.get("Departments") or config.get("departments") or {"general": []},
            "ModelPricing": config.get("ModelPricing") or config.get("modelPricing") or {"mock-model": {"InputPer1KTokens": 0, "OutputPer1KTokens": 0}},
        }

    @staticmethod
    def _mock_grounded_answer(downstream_response: Any) -> str:
        if isinstance(downstream_response, dict):
            message = downstream_response.get("message") or downstream_response.get("summary")
            if message:
                return str(message)
            data = downstream_response.get("data", downstream_response)
            if isinstance(data, list):
                return f"I found {len(data)} matching record(s) from the verified API response."
        if isinstance(downstream_response, list):
            return f"I found {len(downstream_response)} matching record(s) from the verified API response."
        return "I retrieved the verified API response, but no concise summary field was provided."

