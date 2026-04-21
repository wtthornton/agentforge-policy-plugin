"""Deterministic runner for budget-agent. Pure function, no side effects."""

from __future__ import annotations


class BudgetRunner:
    def run(self, input_text: str) -> str:
        return "budget:ok"
