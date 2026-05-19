from __future__ import annotations

import re
from typing import Any

from app.models.config_models import ApiConfig, ApiRegistry


class IntentDecision:
    def __init__(
        self,
        api_config: ApiConfig | None,
        intent: str,
        parameters: dict[str, Any],
        missing_fields: list[str],
        tags: list[str],
    ) -> None:
        self.api_config = api_config
        self.intent = intent
        self.parameters = parameters
        self.missing_fields = missing_fields
        self.tags = tags


class IntentService:
    def select_intent(
        self,
        message: str,
        api_registry_config: Any,
        user_id: str,
        memory_entities: dict[str, Any],
    ) -> IntentDecision:
        registry = ApiRegistry.model_validate(api_registry_config or {"apis": []})
        selected = self._select_api(message, registry.apis)
        if selected is None:
            return IntentDecision(None, "unknown", {}, ["intent"], ["clarification"])

        parameters = dict(memory_entities)
        parameters.update(self._extract_parameters(message, selected, user_id))
        missing = [name for name in selected.required_parameters if parameters.get(name) in {None, ""}]
        tags = list(dict.fromkeys([*(selected.tags or []), selected.intent or selected.api_name]))
        return IntentDecision(selected, selected.intent or selected.api_name, parameters, missing, tags)

    @staticmethod
    def _select_api(message: str, apis: list[ApiConfig]) -> ApiConfig | None:
        normalized = message.lower()
        best: tuple[int, ApiConfig] | None = None
        for api in apis:
            keywords = [keyword.lower() for keyword in api.intent_keywords]
            score = sum(1 for keyword in keywords if keyword in normalized)
            if score and (best is None or score > best[0]):
                best = (score, api)
        return best[1] if best else (apis[0] if len(apis) == 1 else None)

    @staticmethod
    def _extract_parameters(message: str, api: ApiConfig, user_id: str) -> dict[str, Any]:
        params: dict[str, Any] = {}
        current_year_match = re.search(r"\b(20\d{2}|19\d{2})\b", message)
        for target, rule in api.parameter_mapping.items():
            if rule == "userId":
                params[target] = user_id
            elif rule == "year" and current_year_match:
                year = current_year_match.group(1)
                params[target] = year
                params.setdefault("startDateFrom", f"{year}-01-01")
                params.setdefault("startDateTo", f"{year}-12-31")
            elif isinstance(rule, dict):
                if "default" in rule:
                    params[target] = rule["default"]
                pattern = rule.get("regex")
                if pattern:
                    match = re.search(str(pattern), message, flags=re.IGNORECASE)
                    if match:
                        params[target] = match.group(1) if match.groups() else match.group(0)
                values = rule.get("values")
                if isinstance(values, dict):
                    lower_message = message.lower()
                    for text, value in values.items():
                        if str(text).lower() in lower_message:
                            params[target] = value
        return params

