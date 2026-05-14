"""Tests for LLMClient and config/logging."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from llm_platform_library import LLMClient, LLMMessage
from llm_platform_library.client import validate_config
from llm_platform_library.exceptions import (
    ConfigFileNotFoundError,
    InvalidConfigJsonError,
    InvalidConfigValueError,
    LLMProviderError,
    MissingConfigKeyError,
)
from llm_platform_library.logger import get_log_file_name


@pytest.fixture
def valid_config(tmp_path: Path) -> dict[str, object]:
    return {
        "Provider": "mock",
        "DefaultModel": "gpt-4.1-mini",
        "LogLocation": str(tmp_path / "logs"),
        "PromptFolder": "prompts",
        "Departments": {
            "HR": ["leave", "salary"],
            "Finance": ["invoice"],
            "IT": ["password"],
            "Legal": ["contract"],
            "Sales": ["lead"],
            "General": [],
        },
        "ModelPricing": {
            "gpt-4.1-mini": {
                "InputPer1KTokens": 0.00015,
                "OutputPer1KTokens": 0.0006,
            }
        },
    }


@pytest.fixture
def config_file(tmp_path: Path, valid_config: dict[str, object]) -> Path:
    path = tmp_path / "config.json"
    path.write_text(json.dumps(valid_config), encoding="utf-8")
    return path


def test_mock_response(config_file: Path) -> None:
    client = LLMClient(config_file)

    response = client.generate_response("Hello", department="HR")

    assert response.content == "Mock response generated successfully."
    assert response.model == "gpt-4.1-mini"
    assert response.department == "HR"
    assert response.usage.total_tokens > 0


def test_generate_response_with_messages(config_file: Path) -> None:
    client = LLMClient(config_file)

    response = client.generate_response_with_messages(
        [LLMMessage(role="user", content="hello")]
    )

    assert response.provider == "mock"


def test_empty_messages_raise(config_file: Path) -> None:
    client = LLMClient(config_file)

    with pytest.raises(InvalidConfigValueError):
        client.generate_response_with_messages([])


def test_invalid_prompt_raises(config_file: Path) -> None:
    client = LLMClient(config_file)

    with pytest.raises(InvalidConfigValueError):
        client.generate_response("")


def test_provider_error_handling(valid_config: dict[str, object]) -> None:
    valid_config["Provider"] = "azure_openai"
    client = LLMClient(config_data=valid_config)

    with pytest.raises(LLMProviderError):
        client.generate_response("hello")


def test_config_load_success_creates_logger(
    config_file: Path,
    valid_config: dict[str, object],
) -> None:
    LLMClient(config_file)

    log_file = Path(str(valid_config["LogLocation"])) / get_log_file_name()
    assert log_file.is_file()


def test_missing_config_raises(tmp_path: Path) -> None:
    with pytest.raises(ConfigFileNotFoundError):
        LLMClient(tmp_path / "missing.json")


def test_invalid_json_raises(tmp_path: Path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text("{ invalid", encoding="utf-8")

    with pytest.raises(InvalidConfigJsonError):
        LLMClient(config_file)


def test_missing_required_config_key(valid_config: dict[str, object]) -> None:
    valid_config.pop("Provider")

    with pytest.raises(MissingConfigKeyError):
        validate_config(valid_config)


def test_invalid_departments_type(valid_config: dict[str, object]) -> None:
    valid_config["Departments"] = []

    with pytest.raises(InvalidConfigValueError):
        validate_config(valid_config)


def test_invalid_model_pricing_type(valid_config: dict[str, object]) -> None:
    valid_config["ModelPricing"] = []

    with pytest.raises(InvalidConfigValueError):
        validate_config(valid_config)


def test_invalid_config_root_from_file(tmp_path: Path) -> None:
    config_file = tmp_path / "config.json"
    config_file.write_text("[1, 2, 3]", encoding="utf-8")

    with pytest.raises(InvalidConfigValueError):
        LLMClient(config_file)
