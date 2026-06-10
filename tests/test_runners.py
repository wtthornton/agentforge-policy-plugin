"""Unit tests for policy-plugin deterministic runners."""

from __future__ import annotations

from agentforge_policy.agents.budget_agent.runner import BudgetRunner
from agentforge_policy.agents.low_risk_agent.runner import LowRiskRunner
from agentforge_policy.agents.no_completion_agent.runner import NoCompletionRunner
from agentforge_policy.agents.risky_agent.runner import RiskyRunner


def test_risky_runner_returns_ok() -> None:
    runner = RiskyRunner()
    assert runner.run("anything") == "risky:ok"


def test_budget_runner_returns_ok() -> None:
    runner = BudgetRunner()
    assert runner.run("anything") == "budget:ok"


def test_low_risk_runner_returns_invoke_ok() -> None:
    assert LowRiskRunner().run("anything") == "invoke:ok"


def test_no_completion_runner_returns_drift() -> None:
    """Runner output intentionally misses the declared completion criteria."""
    assert NoCompletionRunner().run("anything") == "drift"
