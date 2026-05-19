"""Dataclass models used by llm_platform_library."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LLMMessage:
    """A chat message sent to an LLM provider."""

    role: str
    content: str


@dataclass(frozen=True, slots=True)
class TokenUsage:
    """Token usage metadata for one LLM request."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass(frozen=True, slots=True)
class LLMResponse:
    """Structured LLM response returned to consuming applications."""

    content: str
    model: str
    provider: str
    usage: TokenUsage
    department: str | None = None


@dataclass(frozen=True, slots=True)
class RAGDocument:
    """Retrieved document metadata used to ground an answer."""

    document_id: str
    content: str
    metadata: dict[str, str] | None = None


@dataclass(frozen=True, slots=True)
class RAGResponse:
    """Grounded answer with source document IDs."""

    answer: str
    source_document_ids: tuple[str, ...]
    llm_response: LLMResponse


@dataclass(frozen=True, slots=True)
class DepartmentRoute:
    """Department routing decision."""

    department: str
    confidence: float
    matched_keywords: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PromptTemplate:
    """Named prompt template."""

    name: str
    template: str


@dataclass(frozen=True, slots=True)
class ModelPricing:
    """Model pricing per 1,000 input and output tokens."""

    input_per_1k_tokens: float
    output_per_1k_tokens: float


@dataclass(frozen=True, slots=True)
class LLMPlatformConfig:
    """Validated library configuration."""

    provider: str
    default_model: str
    log_location: str
    prompt_folder: str
    departments: dict[str, tuple[str, ...]]
    model_pricing: dict[str, ModelPricing]

