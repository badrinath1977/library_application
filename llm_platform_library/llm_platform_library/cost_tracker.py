"""Token usage and cost tracking."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from llm_platform_library.exceptions import CostTrackingError
from llm_platform_library.logger import get_bootstrap_logger
from llm_platform_library.models import ModelPricing, TokenUsage


@dataclass(slots=True)
class _UsageRecord:
    usage: TokenUsage
    department: str
    model: str
    cost: float


class CostTracker:
    """Track usage and estimated cost by department and model."""

    def __init__(
        self,
        model_pricing: dict[str, ModelPricing],
        logger: logging.Logger | None = None,
    ) -> None:
        self._logger = logger or get_bootstrap_logger()
        self._model_pricing = dict(model_pricing)
        self._records: list[_UsageRecord] = []

    def record_usage(self, usage: TokenUsage, department: str, model: str) -> None:
        """Record token usage and estimated cost."""

        self._logger.debug(
            "event=record_usage_start department=%s model=%s",
            department,
            model,
        )
        if model not in self._model_pricing:
            self._logger.exception(
                "event=cost_model_missing status=failure model=%s",
                model,
            )
            raise CostTrackingError(f"No pricing configured for model '{model}'.")
        if usage.prompt_tokens < 0 or usage.completion_tokens < 0:
            self._logger.exception("event=cost_usage_invalid status=failure")
            raise CostTrackingError("Token usage values must be non-negative.")

        pricing = self._model_pricing[model]
        cost = (
            usage.prompt_tokens / 1000 * pricing.input_per_1k_tokens
            + usage.completion_tokens / 1000 * pricing.output_per_1k_tokens
        )
        self._records.append(
            _UsageRecord(
                usage=usage,
                department=department,
                model=model,
                cost=cost,
            )
        )
        self._logger.info(
            "event=usage_recorded status=success department=%s model=%s",
            department,
            model,
        )
        self._logger.debug("event=record_usage_end")

    def get_total_cost(self) -> float:
        """Return total estimated cost."""

        return sum(record.cost for record in self._records)

    def get_department_cost(self, department: str) -> float:
        """Return estimated cost for a department."""

        return sum(
            record.cost for record in self._records if record.department == department
        )

    def get_model_cost(self, model: str) -> float:
        """Return estimated cost for a model."""

        return sum(record.cost for record in self._records if record.model == model)

    def export_usage_report(self) -> dict[str, object]:
        """Export usage report as a plain dictionary."""

        return {
            "total_cost": self.get_total_cost(),
            "records": [
                {
                    "department": record.department,
                    "model": record.model,
                    "prompt_tokens": record.usage.prompt_tokens,
                    "completion_tokens": record.usage.completion_tokens,
                    "total_tokens": record.usage.total_tokens,
                    "cost": record.cost,
                }
                for record in self._records
            ],
        }
