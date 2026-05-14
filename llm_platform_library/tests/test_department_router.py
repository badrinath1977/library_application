"""Tests for DepartmentRouter."""

import pytest

from llm_platform_library import DepartmentRouter
from llm_platform_library.exceptions import RoutingError


@pytest.fixture
def router() -> DepartmentRouter:
    return DepartmentRouter(
        {
            "HR": ["leave", "salary", "benefits", "policy"],
            "Finance": ["invoice", "budget", "expense", "payment"],
            "IT": ["password", "access", "laptop", "vpn"],
            "Legal": ["contract", "agreement", "compliance"],
            "Sales": ["lead", "customer", "pricing", "proposal"],
            "General": [],
        }
    )


def test_hr_routing(router: DepartmentRouter) -> None:
    assert router.route("What is the leave policy?").department == "HR"


def test_finance_routing(router: DepartmentRouter) -> None:
    assert router.route("Need invoice payment status").department == "Finance"


def test_it_routing(router: DepartmentRouter) -> None:
    assert router.route("Need vpn access").department == "IT"


def test_legal_routing(router: DepartmentRouter) -> None:
    assert router.route("Review this contract agreement").department == "Legal"


def test_sales_routing(router: DepartmentRouter) -> None:
    assert router.route("Customer pricing proposal").department == "Sales"


def test_fallback_to_general(router: DepartmentRouter) -> None:
    assert router.route("What time is lunch?").department == "General"


def test_confidence_score(router: DepartmentRouter) -> None:
    route = router.route("leave salary benefits policy")

    assert route.confidence == pytest.approx(1.0)
    assert route.matched_keywords == ("leave", "salary", "benefits", "policy")


def test_add_rule() -> None:
    router = DepartmentRouter()
    router.add_rule("Security", ["phishing"])

    assert router.route("phishing report").department == "Security"


def test_invalid_query_raises(router: DepartmentRouter) -> None:
    with pytest.raises(RoutingError):
        router.route("")


def test_invalid_department_rule_raises() -> None:
    router = DepartmentRouter()

    with pytest.raises(RoutingError):
        router.add_rule("", ["keyword"])


def test_invalid_keyword_rule_raises() -> None:
    router = DepartmentRouter()

    with pytest.raises(RoutingError):
        router.add_rule("HR", ["leave", 1])  # type: ignore[list-item]
