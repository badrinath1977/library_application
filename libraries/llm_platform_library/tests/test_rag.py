"""Tests for RAGService."""

from __future__ import annotations

from pathlib import Path

import pytest

from llm_platform_library import LLMClient, RAGDocument, RAGService
from libraries.llm_platform_library.llm_platform_library.exceptions import RAGError


@pytest.fixture
def client_config(tmp_path: Path) -> dict[str, object]:
    return {
        "Provider": "mock",
        "DefaultModel": "gpt-4.1-mini",
        "LogLocation": str(tmp_path / "logs"),
        "PromptFolder": "prompts",
        "Departments": {"General": []},
        "ModelPricing": {
            "gpt-4.1-mini": {
                "InputPer1KTokens": 0.00015,
                "OutputPer1KTokens": 0.0006,
            }
        },
    }


def test_context_building(client_config: dict[str, object]) -> None:
    service = RAGService(LLMClient(config_data=client_config))

    context = service.build_context(
        [
            RAGDocument(document_id="doc1", content="First"),
            RAGDocument(document_id="doc2", content="Second"),
        ]
    )

    assert "[doc1]" in context
    assert "Second" in context


def test_answer_generation(client_config: dict[str, object]) -> None:
    service = RAGService(LLMClient(config_data=client_config))

    response = service.generate_answer(
        "What is the policy?",
        [RAGDocument(document_id="doc1", content="Policy content")],
    )

    assert response.answer == "Mock response generated successfully."
    assert response.source_document_ids == ("doc1",)


def test_empty_document_handling(client_config: dict[str, object]) -> None:
    service = RAGService(LLMClient(config_data=client_config))

    response = service.generate_answer("Question?", [])

    assert response.source_document_ids == ()


def test_invalid_query_raises(client_config: dict[str, object]) -> None:
    service = RAGService(LLMClient(config_data=client_config))

    with pytest.raises(RAGError):
        service.generate_answer("", [])

