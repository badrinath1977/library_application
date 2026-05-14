"""Tests for CostTracker."""

import pytest

from llm_platform_library import CostTracker, ModelPricing, TokenUsage
from llm_platform_library.exceptions import CostTrackingError


def test_record_usage() -> None:
    tracker = CostTracker({"gpt-4.1-mini": ModelPricing(0.00015, 0.0006)})

    tracker.record_usage(TokenUsage(1000, 1000, 2000), "HR", "gpt-4.1-mini")

    assert tracker.get_total_cost() == pytest.approx(0.00075)


def test_total_cost() -> None:
    tracker = CostTracker({"gpt-4.1-mini": ModelPricing(1.0, 2.0)})
    tracker.record_usage(TokenUsage(1000, 500, 1500), "HR", "gpt-4.1-mini")

    assert tracker.get_total_cost() == pytest.approx(2.0)


def test_department_cost() -> None:
    tracker = CostTracker({"gpt-4.1-mini": ModelPricing(1.0, 1.0)})
    tracker.record_usage(TokenUsage(1000, 0, 1000), "HR", "gpt-4.1-mini")
    tracker.record_usage(TokenUsage(1000, 0, 1000), "IT", "gpt-4.1-mini")

    assert tracker.get_department_cost("HR") == pytest.approx(1.0)


def test_model_cost() -> None:
    tracker = CostTracker(
        {
            "gpt-4.1-mini": ModelPricing(1.0, 1.0),
            "other": ModelPricing(2.0, 1.0),
        }
    )
    tracker.record_usage(TokenUsage(1000, 0, 1000), "HR", "gpt-4.1-mini")
    tracker.record_usage(TokenUsage(1000, 0, 1000), "HR", "other")

    assert tracker.get_model_cost("other") == pytest.approx(2.0)


def test_export_report() -> None:
    tracker = CostTracker({"gpt-4.1-mini": ModelPricing(1.0, 1.0)})
    tracker.record_usage(TokenUsage(1000, 0, 1000), "HR", "gpt-4.1-mini")

    report = tracker.export_usage_report()

    assert report["total_cost"] == pytest.approx(1.0)
    assert len(report["records"]) == 1


def test_missing_model_pricing_raises() -> None:
    tracker = CostTracker({})

    with pytest.raises(CostTrackingError):
        tracker.record_usage(TokenUsage(1, 1, 2), "HR", "missing")


def test_negative_usage_raises() -> None:
    tracker = CostTracker({"gpt-4.1-mini": ModelPricing(1.0, 1.0)})

    with pytest.raises(CostTrackingError):
        tracker.record_usage(TokenUsage(-1, 1, 0), "HR", "gpt-4.1-mini")
