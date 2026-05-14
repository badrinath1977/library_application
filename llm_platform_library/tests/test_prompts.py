"""Tests for PromptManager."""

import pytest

from llm_platform_library import PromptManager
from llm_platform_library.exceptions import PromptNotFoundError, PromptRenderError


def test_register_prompt() -> None:
    manager = PromptManager()

    manager.register_prompt("hello", "Hello {name}")

    assert manager.get_prompt("hello") == "Hello {name}"


def test_get_prompt() -> None:
    manager = PromptManager({"summary": "Summarize {text}"})

    assert manager.get_prompt("summary") == "Summarize {text}"


def test_render_prompt() -> None:
    manager = PromptManager({"summary": "Summarize {text}"})

    rendered = manager.render_prompt("summary", {"text": "content"})

    assert rendered == "Summarize content"


def test_missing_prompt_error() -> None:
    manager = PromptManager()

    with pytest.raises(PromptNotFoundError):
        manager.get_prompt("missing")


def test_missing_variable_error() -> None:
    manager = PromptManager({"summary": "Summarize {text}"})

    with pytest.raises(PromptRenderError):
        manager.render_prompt("summary", {})


def test_register_invalid_prompt_raises() -> None:
    manager = PromptManager()

    with pytest.raises(PromptRenderError):
        manager.register_prompt("", "template")


def test_render_invalid_template_raises() -> None:
    manager = PromptManager({"bad": "Value: {broken"})

    with pytest.raises(PromptRenderError):
        manager.render_prompt("bad", {"broken": "value"})
