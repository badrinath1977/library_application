"""LLM client and configuration loading."""

from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from libraries.llm_platform_library.llm_platform_library.exceptions import (
    ConfigFileNotFoundError,
    InvalidConfigJsonError,
    InvalidConfigValueError,
    LLMPlatformLibraryError,
    LLMProviderError,
    MissingConfigKeyError,
)
from libraries.llm_platform_library.llm_platform_library.logger import create_library_logger, get_bootstrap_logger
from libraries.llm_platform_library.llm_platform_library.models import (
    LLMMessage,
    LLMPlatformConfig,
    LLMResponse,
    ModelPricing,
    TokenUsage,
)

REQUIRED_CONFIG_KEYS = (
    "Provider",
    "DefaultModel",
    "LogLocation",
    "PromptFolder",
    "Departments",
    "ModelPricing",
)


class LLMClient:
    """Provider-abstracted LLM client.

    The current implementation supports a safe mock provider only. Real Azure
    OpenAI or OpenAI-style providers can be added behind this interface without
    changing consuming application code.
    """

    def __init__(
        self,
        config_path: str | Path = "config.json",
        config_data: Mapping[str, Any] | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self._config_path = Path(config_path)
        self._logger = logger or get_bootstrap_logger()
        self._logger.debug("event=llm_client_init_start")

        raw_config = (
            dict(config_data) if config_data is not None else self._load_config()
        )
        self.config = validate_config(raw_config)
        self._logger = logger or create_library_logger(self.config.log_location)
        self._logger.info(
            "event=llm_client_config_loaded status=success provider=%s model=%s",
            self.config.provider,
            self.config.default_model,
        )
        self._logger.debug("event=llm_client_init_end")

    @classmethod
    def from_dict(cls, config_data: Mapping[str, Any]) -> LLMClient:
        """Create a client from application-owned configuration data."""

        return cls(config_data=config_data)

    def generate_response(
        self,
        prompt: str,
        department: str | None = None,
    ) -> LLMResponse:
        """Generate a response for a single prompt."""

        self._logger.debug("event=generate_response_start department=%s", department)
        if not isinstance(prompt, str) or not prompt.strip():
            self._logger.error("event=invalid_prompt status=failure")
            raise InvalidConfigValueError("Prompt must be a non-empty string.")

        response = self.generate_response_with_messages(
            [LLMMessage(role="user", content=prompt)],
        )
        self._logger.debug("event=generate_response_end")
        return LLMResponse(
            content=response.content,
            model=response.model,
            provider=response.provider,
            usage=response.usage,
            department=department,
        )

    def generate_response_with_messages(
        self,
        messages: list[LLMMessage],
    ) -> LLMResponse:
        """Generate a response from chat-style messages."""

        self._logger.debug("event=generate_response_with_messages_start")
        if not messages:
            self._logger.error("event=invalid_messages status=failure")
            raise InvalidConfigValueError("Messages must not be empty.")

        try:
            if self.config.provider.lower() != "mock":
                raise LLMProviderError(
                    f"Provider '{self.config.provider}' is not implemented."
                )

            prompt_text = "\n".join(message.content for message in messages)
            usage = _estimate_usage(prompt_text)
            self._logger.info(
                "event=llm_mock_response status=success model=%s message_count=%d",
                self.config.default_model,
                len(messages),
            )
            return LLMResponse(
                content="Mock response generated successfully.",
                model=self.config.default_model,
                provider=self.config.provider,
                usage=usage,
            )
        except LLMProviderError:
            self._logger.exception("event=llm_provider_error status=failure")
            raise
        except (TypeError, ValueError) as exc:
            self._logger.exception("event=llm_provider_unexpected_error status=failure")
            raise LLMProviderError("LLM provider request failed.") from exc
        finally:
            self._logger.debug("event=generate_response_with_messages_end")

    def _load_config(self) -> dict[str, Any]:
        """Load JSON config from disk."""

        try:
            with self._config_path.open("r", encoding="utf-8") as config_file:
                try:
                    payload = json.load(config_file)
                except json.JSONDecodeError as exc:
                    self._logger.exception("event=config_json_invalid status=failure")
                    raise InvalidConfigJsonError(
                        "Configuration JSON is invalid."
                    ) from exc
        except FileNotFoundError as exc:
            self._logger.exception(
                "event=config_file_missing status=failure path=%s",
                self._config_path,
            )
            raise ConfigFileNotFoundError(
                f"Configuration file was not found: '{self._config_path}'."
            ) from exc
        except OSError as exc:
            self._logger.exception("event=config_file_read_failed status=failure")
            raise LLMPlatformLibraryError(
                "Configuration file could not be read."
            ) from exc

        if not isinstance(payload, dict):
            self._logger.error("event=config_root_invalid status=failure")
            raise InvalidConfigValueError("Configuration root must be a JSON object.")
        return payload


def validate_config(payload: Mapping[str, Any]) -> LLMPlatformConfig:
    """Validate raw configuration and return an immutable config model."""

    for key in REQUIRED_CONFIG_KEYS:
        if key not in payload:
            raise MissingConfigKeyError(f"Missing required configuration key: '{key}'.")

    provider = _required_string(payload["Provider"], "Provider")
    default_model = _required_string(payload["DefaultModel"], "DefaultModel")
    log_location = _required_string(payload["LogLocation"], "LogLocation")
    prompt_folder = _required_string(payload["PromptFolder"], "PromptFolder")
    departments = _validate_departments(payload["Departments"])
    pricing = _validate_model_pricing(payload["ModelPricing"])

    return LLMPlatformConfig(
        provider=provider,
        default_model=default_model,
        log_location=log_location,
        prompt_folder=prompt_folder,
        departments=departments,
        model_pricing=pricing,
    )


def _required_string(value: Any, key: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InvalidConfigValueError(f"Configuration key '{key}' must be a string.")
    return value


def _validate_departments(value: Any) -> dict[str, tuple[str, ...]]:
    if not isinstance(value, dict):
        raise InvalidConfigValueError("Departments must be an object.")
    departments: dict[str, tuple[str, ...]] = {}
    for department, keywords in value.items():
        if not isinstance(department, str) or not isinstance(keywords, list):
            raise InvalidConfigValueError("Departments must map strings to lists.")
        if any(not isinstance(keyword, str) for keyword in keywords):
            raise InvalidConfigValueError("Department keywords must be strings.")
        departments[department] = tuple(keywords)
    return departments


def _validate_model_pricing(value: Any) -> dict[str, ModelPricing]:
    if not isinstance(value, dict):
        raise InvalidConfigValueError("ModelPricing must be an object.")
    pricing: dict[str, ModelPricing] = {}
    for model, model_pricing in value.items():
        if not isinstance(model, str) or not isinstance(model_pricing, dict):
            raise InvalidConfigValueError("ModelPricing must map models to pricing.")
        input_price = model_pricing.get("InputPer1KTokens")
        output_price = model_pricing.get("OutputPer1KTokens")
        if not isinstance(input_price, int | float) or not isinstance(
            output_price,
            int | float,
        ):
            raise InvalidConfigValueError("Model pricing values must be numeric.")
        pricing[model] = ModelPricing(float(input_price), float(output_price))
    return pricing


def _estimate_usage(prompt_text: str) -> TokenUsage:
    prompt_tokens = max(1, len(prompt_text.split()))
    completion_tokens = max(1, min(50, prompt_tokens // 2 + 1))
    return TokenUsage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=prompt_tokens + completion_tokens,
    )
