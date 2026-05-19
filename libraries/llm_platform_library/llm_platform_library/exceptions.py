"""Custom exception hierarchy for llm_platform_library."""


class LLMPlatformLibraryError(Exception):
    """Base exception for all expected llm_platform_library failures."""


class ConfigFileNotFoundError(LLMPlatformLibraryError):
    """Raised when the configuration file cannot be found."""


class InvalidConfigJsonError(LLMPlatformLibraryError):
    """Raised when the configuration file contains invalid JSON."""


class MissingConfigKeyError(LLMPlatformLibraryError):
    """Raised when a required configuration key is missing."""


class InvalidConfigValueError(LLMPlatformLibraryError):
    """Raised when a configuration value is invalid."""


class PromptNotFoundError(LLMPlatformLibraryError):
    """Raised when a prompt template cannot be found."""


class PromptRenderError(LLMPlatformLibraryError):
    """Raised when a prompt cannot be rendered safely."""


class RoutingError(LLMPlatformLibraryError):
    """Raised when department routing fails."""


class CostTrackingError(LLMPlatformLibraryError):
    """Raised when usage cannot be recorded or priced."""


class LLMProviderError(LLMPlatformLibraryError):
    """Raised when the configured LLM provider cannot handle a request."""


class RAGError(LLMPlatformLibraryError):
    """Raised when RAG answer generation fails."""


class LoggerSetupError(LLMPlatformLibraryError):
    """Raised when logging cannot be initialized."""

