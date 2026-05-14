"""Tests for exception hierarchy."""

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


def test_custom_exceptions_inherit_from_base() -> None:
    exception_types = (
        ConfigFileNotFoundError,
        InvalidConfigJsonError,
        MissingConfigKeyError,
        InvalidConfigValueError,
        PromptNotFoundError,
        PromptRenderError,
        RoutingError,
        CostTrackingError,
        LLMProviderError,
        RAGError,
        LoggerSetupError,
    )

    for exception_type in exception_types:
        assert issubclass(exception_type, LLMPlatformLibraryError)

