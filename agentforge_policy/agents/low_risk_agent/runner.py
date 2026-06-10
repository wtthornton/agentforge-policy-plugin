"""Deterministic runner for low-risk-agent. Returns a fixed sentinel."""

from __future__ import annotations


class LowRiskRunner:
    def run(self, input_text: str) -> str:
        return "invoke:ok"
