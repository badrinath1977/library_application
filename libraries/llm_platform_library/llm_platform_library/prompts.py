"""Prompt management utilities."""

from __future__ import annotations

import logging
from string import Formatter

from libraries.llm_platform_library.llm_platform_library.exceptions import PromptNotFoundError, PromptRenderError
from libraries.llm_platform_library.llm_platform_library.logger import get_bootstrap_logger
from libraries.llm_platform_library.llm_platform_library.models import PromptTemplate


class PromptManager:
    """Manage named and department-specific prompt templates."""

    def __init__(
        self,
        prompts: dict[str, str] | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self._logger = logger or get_bootstrap_logger()
        self._prompts: dict[str, PromptTemplate] = {}
        for name, template in (prompts or {}).items():
            self.register_prompt(name, template)

    def get_prompt(self, name: str) -> str:
        """Return a prompt template by name."""

        self._logger.debug("event=get_prompt_start name=%s", name)
        try:
            prompt = self._prompts[name].template
        except KeyError as exc:
            self._logger.exception(
                "event=prompt_not_found status=failure name=%s",
                name,
            )
            raise PromptNotFoundError(f"Prompt '{name}' was not found.") from exc
        self._logger.debug("event=get_prompt_end name=%s", name)
        return prompt

    def render_prompt(self, name: str, variables: dict[str, str]) -> str:
        """Render a prompt safely with required variables."""

        self._logger.debug("event=render_prompt_start name=%s", name)
        template = self.get_prompt(name)
        try:
            required_variables = _extract_placeholders(template)
        except ValueError as exc:
            self._logger.exception(
                "event=prompt_placeholder_parse_failed status=failure name=%s",
                name,
            )
            raise PromptRenderError(
                f"Prompt '{name}' contains invalid placeholder syntax."
            ) from exc
        missing_variables = required_variables - variables.keys()
        if missing_variables:
            self._logger.exception(
                "event=prompt_render_missing_variables status=failure name=%s",
                name,
            )
            raise PromptRenderError(
                f"Prompt '{name}' is missing variables: "
                f"{', '.join(sorted(missing_variables))}."
            )

        try:
            rendered_prompt = template.format(**variables)
        except (KeyError, ValueError) as exc:
            self._logger.exception(
                "event=prompt_render_failed status=failure name=%s",
                name,
            )
            raise PromptRenderError(f"Prompt '{name}' could not be rendered.") from exc

        self._logger.debug("event=render_prompt_end name=%s", name)
        return rendered_prompt

    def register_prompt(self, name: str, template: str) -> None:
        """Register or replace a named prompt template."""

        self._logger.debug("event=register_prompt_start name=%s", name)
        if not name.strip() or not template.strip():
            self._logger.error("event=register_prompt_invalid status=failure")
            raise PromptRenderError("Prompt name and template must be non-empty.")
        self._prompts[name] = PromptTemplate(name=name, template=template)
        self._logger.info("event=prompt_registered status=success name=%s", name)
        self._logger.debug("event=register_prompt_end name=%s", name)


def _extract_placeholders(template: str) -> set[str]:
    """Return field names used by a format template."""

    placeholders: set[str] = set()
    for _, field_name, _, _ in Formatter().parse(template):
        if field_name:
            placeholders.add(field_name)
    return placeholders
