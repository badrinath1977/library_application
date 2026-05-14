"""Public interface for llm_platform_library."""

from llm_platform_library.client import LLMClient
from llm_platform_library.cost_tracker import CostTracker
from llm_platform_library.department_router import DepartmentRouter
from llm_platform_library.exceptions import (
    ConfigFileNotFoundError,
    CostTrackingError,
    InvalidConfigJsonError,
    InvalidConfigValueError,
    LLMPlatformLibraryError,
    LLMProviderError,
    LoggerSetupError,
    MissingConfigKeyError,
    PromptNotFoundError,
    PromptRenderError,
    RAGError,
    RoutingError,
)
from llm_platform_library.models import (
    DepartmentRoute,
    LLMMessage,
    LLMResponse,
    ModelPricing,
    PromptTemplate,
    RAGDocument,
    RAGResponse,
    TokenUsage,
)
from llm_platform_library.prompts import PromptManager
from llm_platform_library.rag import RAGService

__all__ = [
    "ConfigFileNotFoundError",
    "CostTracker",
    "CostTrackingError",
    "DepartmentRoute",
    "DepartmentRouter",
    "InvalidConfigJsonError",
    "InvalidConfigValueError",
    "LLMClient",
    "LLMMessage",
    "LLMPlatformLibraryError",
    "LLMProviderError",
    "LLMResponse",
    "LoggerSetupError",
    "MissingConfigKeyError",
    "ModelPricing",
    "PromptManager",
    "PromptNotFoundError",
    "PromptRenderError",
    "PromptTemplate",
    "RAGDocument",
    "RAGError",
    "RAGResponse",
    "RAGService",
    "RoutingError",
    "TokenUsage",
]

