"""Error grouping and root-cause analysis."""

from __future__ import annotations

from collections import defaultdict

from app.models.response_models import ErrorAnalysisResponse
from app.services.log_parser import ParsedError

FRAMEWORK_HINTS = (
    "site-packages",
    "node_modules",
    "System.",
    "Microsoft.",
    "org.springframework",
    "java.",
)


class ErrorAnalyzer:
    """Group duplicate errors and infer root cause hints."""

    def analyze(self, parsed_errors: list[ParsedError]) -> list[ErrorAnalysisResponse]:
        """Return grouped structured errors."""

        groups: dict[str, list[ParsedError]] = defaultdict(list)
        for error in parsed_errors:
            groups[error.id].append(error)

        results: list[ErrorAnalysisResponse] = []
        for error_id, occurrences in groups.items():
            first = occurrences[0]
            most_recent = max(
                (occurrence.timestamp for occurrence in occurrences if occurrence.timestamp),
                default=None,
            )
            results.append(
                ErrorAnalysisResponse(
                    id=error_id,
                    error_message=first.error_message,
                    exception_type=first.exception_type,
                    stacktrace=first.stacktrace,
                    method_name=first.method_name,
                    file_name=first.file_name,
                    line_number=first.line_number,
                    class_name=first.class_name,
                    module_name=first.module_name,
                    timestamp=first.timestamp,
                    log_level=first.log_level,
                    occurrence_count=len(occurrences),
                    most_recent_occurrence=most_recent or first.timestamp,
                    root_cause_guess=self._guess_root_cause(first),
                    is_application_file=self._is_application_file(first.file_name),
                    raw_error_block=first.raw_error_block,
                )
            )
        return sorted(results, key=lambda item: item.occurrence_count, reverse=True)

    def _guess_root_cause(self, error: ParsedError) -> str | None:
        if error.exception_type and error.error_message:
            return f"{error.exception_type}: {error.error_message}"
        if error.error_message:
            return error.error_message
        return None

    def _is_application_file(self, file_name: str | None) -> bool | None:
        if not file_name:
            return None
        return not any(hint in file_name for hint in FRAMEWORK_HINTS)

