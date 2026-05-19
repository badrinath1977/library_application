from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from app.core.settings import Settings


@dataclass(slots=True)
class ConversationMemory:
    conversation_id: str
    messages: list[dict[str, Any]] = field(default_factory=list)
    summary: str | None = None
    entities: dict[str, Any] = field(default_factory=dict)
    previous_api_execution: dict[str, Any] | None = None
    pending_actions: dict[str, dict[str, Any]] = field(default_factory=dict)


class ConversationMemoryService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._store: dict[str, ConversationMemory] = {}

    def get(self, conversation_id: str) -> ConversationMemory:
        if conversation_id not in self._store:
            self._store[conversation_id] = ConversationMemory(conversation_id=conversation_id)
        return self._store[conversation_id]

    def append_message(self, conversation_id: str, role: str, content: str, metadata: dict[str, Any] | None = None) -> None:
        memory = self.get(conversation_id)
        memory.messages.append(
            {"role": role, "content": content, "metadata": metadata or {}, "createdAt": time.time()}
        )
        if len(memory.messages) > self._settings.max_recent_messages * 3:
            retained = memory.messages[-self._settings.max_recent_messages :]
            memory.summary = self._summarize(memory.messages[:-self._settings.max_recent_messages])
            memory.messages = retained

    def recent_window(self, conversation_id: str) -> list[dict[str, Any]]:
        return self.get(conversation_id).messages[-self._settings.max_recent_messages :]

    def update_context(
        self,
        conversation_id: str,
        *,
        entities: dict[str, Any] | None = None,
        api_execution: dict[str, Any] | None = None,
    ) -> None:
        memory = self.get(conversation_id)
        if entities:
            memory.entities.update({key: value for key, value in entities.items() if value is not None})
        if api_execution:
            memory.previous_api_execution = api_execution

    def store_pending_action(self, conversation_id: str, action: dict[str, Any]) -> str:
        memory = self.get(conversation_id)
        confirmation_id = str(uuid4())
        memory.pending_actions[confirmation_id] = {
            "action": action,
            "expiresAt": time.time() + self._settings.pending_action_ttl_seconds,
        }
        return confirmation_id

    def history_payload(self, conversation_id: str) -> dict[str, Any]:
        memory = self.get(conversation_id)
        return {
            "conversationId": conversation_id,
            "summary": memory.summary,
            "recentMessages": self.recent_window(conversation_id),
            "entities": memory.entities,
            "previousApiExecution": memory.previous_api_execution,
            "pendingActionCount": len(memory.pending_actions),
        }

    @staticmethod
    def _summarize(messages: list[dict[str, Any]]) -> str:
        snippets = [f"{item.get('role')}: {str(item.get('content', ''))[:120]}" for item in messages[-10:]]
        return " | ".join(snippets)

