"""Rule-based department routing."""

from __future__ import annotations

import logging

from llm_platform_library.exceptions import RoutingError
from llm_platform_library.logger import get_bootstrap_logger
from llm_platform_library.models import DepartmentRoute


class DepartmentRouter:
    """Route user queries to departments using keyword rules."""

    def __init__(
        self,
        rules: dict[str, tuple[str, ...] | list[str]] | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self._logger = logger or get_bootstrap_logger()
        self._rules: dict[str, tuple[str, ...]] = {}
        for department, keywords in (rules or {}).items():
            self.add_rule(department, list(keywords))

    def route(self, query: str) -> DepartmentRoute:
        """Route a query to the best matching department."""

        self._logger.debug("event=route_start")
        if not isinstance(query, str) or not query.strip():
            self._logger.exception("event=route_invalid_query status=failure")
            raise RoutingError("Query must be a non-empty string.")

        normalized_query = query.lower()
        best_department = "General"
        best_matches: tuple[str, ...] = ()
        best_confidence = 0.0

        for department, keywords in self._rules.items():
            if department == "General" or not keywords:
                continue
            matches = tuple(
                keyword for keyword in keywords if keyword.lower() in normalized_query
            )
            if len(matches) > len(best_matches):
                best_department = department
                best_matches = matches
                best_confidence = min(1.0, len(matches) / max(1, len(keywords)))

        if best_department == "General":
            self._logger.warning("event=route_fallback department=General")

        self._logger.info(
            "event=route_success department=%s confidence=%.3f",
            best_department,
            best_confidence,
        )
        self._logger.debug("event=route_end")
        return DepartmentRoute(
            department=best_department,
            confidence=best_confidence,
            matched_keywords=best_matches,
        )

    def add_rule(self, department: str, keywords: list[str]) -> None:
        """Add or replace routing keywords for a department."""

        self._logger.debug("event=add_rule_start department=%s", department)
        if not department.strip():
            self._logger.exception("event=add_rule_invalid_department status=failure")
            raise RoutingError("Department must be a non-empty string.")
        if any(not isinstance(keyword, str) for keyword in keywords):
            self._logger.exception("event=add_rule_invalid_keywords status=failure")
            raise RoutingError("Keywords must be strings.")
        self._rules[department] = tuple(
            keyword for keyword in keywords if keyword.strip()
        )
        self._logger.debug("event=add_rule_end department=%s", department)
