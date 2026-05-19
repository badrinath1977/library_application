"""LLM solution suggestion service."""

from __future__ import annotations

import logging

from libraries.LogErrorAnalyzerApp.app.core.config import Settings
from libraries.LogErrorAnalyzerApp.app.core.exceptions import LLMServiceError
from libraries.LogErrorAnalyzerApp.app.models.response_models import ErrorAnalysisResponse

logger = logging.getLogger(__name__)


class LLMService:
    """Generate solution suggestions for analyzed errors."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def suggest_solution(self, error: ErrorAnalysisResponse) -> str:
        """Return an LLM solution suggestion."""

        try:
            if self._settings.llm_provider == "mock":
                return self._mock_solution(error)
            if not self._settings.llm_api_key:
                raise LLMServiceError("LLM API key is not configured.")
            raise LLMServiceError(
                f"LLM provider '{self._settings.llm_provider}' is not implemented."
            )
        except LLMServiceError:
            logger.exception("LLM solution generation failed for error_id=%s", error.id)
            raise

    def build_prompt(self, error: ErrorAnalysisResponse) -> str:
        """Build a safe LLM prompt without secrets."""

        return (
            "Analyze this application error. Provide root cause, explanation, "
            "fix recommendation, code-level solution, prevention steps, and "
            "priority/severity.\n\n"
            f"Exception: {error.exception_type}\n"
            f"Message: {error.error_message}\n"
            f"File: {error.file_name}\n"
            f"Method: {error.method_name}\n"
            f"Line: {error.line_number}\n"
            f"Stack trace:\n{error.stacktrace}"
        )

    def _mock_solution(self, error: ErrorAnalysisResponse) -> str:
        severity = "High" if error.exception_type else "Medium"
        return (
            f"Severity: {severity}\n"
            f"Root cause: {error.root_cause_guess or 'Unknown from available logs'}\n"
            "Explanation: The failure occurred in the reported stack frame.\n"
            "Fix recommendation: Inspect the file, method, and line number shown; "
            "add validation and targeted tests around this code path.\n"
            "Code-level solution: Reproduce with the same input and guard null, "
            "type, IO, or dependency failures before the failing call.\n"
            "Prevention: Add structured exception handling, monitoring, and "
            "regression tests for this scenario."
        )

