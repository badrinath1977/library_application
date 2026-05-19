"""Smoke test for llm_platform_library installed from libraries-dist."""

from __future__ import annotations

from llm_platform_library import CostTracker, DepartmentRouter, ModelPricing, PromptManager, TokenUsage


def run() -> str:
    router = DepartmentRouter({"Finance": ["loan", "payment"], "Support": ["ticket"]})
    route = router.route("Need help with loan payment")

    prompts = PromptManager({"greeting": "Hello {name}, route={department}"})
    rendered = prompts.render_prompt(
        "greeting",
        {"name": "Badri", "department": route.department},
    )

    tracker = CostTracker({"demo-model": ModelPricing(0.01, 0.02)})
    tracker.record_usage(TokenUsage(100, 50, 150), route.department, "demo-model")

    return (
        "PASS llm_platform_library: "
        f"department={route.department} "
        f"prompt='{rendered}' "
        f"cost={tracker.get_total_cost():.4f}"
    )


if __name__ == "__main__":
    print(run())
