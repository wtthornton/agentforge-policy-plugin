"""Unit tests for policy-plugin deterministic runners."""

from __future__ import annotations

from agentforge_policy.agents.budget_agent.runner import BudgetRunner
from agentforge_policy.agents.risky_agent.runner import RiskyRunner


def test_risky_runner_returns_ok() -> None:
    runner = RiskyRunner()
    assert runner.run("anything") == "risky:ok"


def test_budget_runner_returns_ok() -> None:
    runner = BudgetRunner()
    assert runner.run("anything") == "budget:ok"
