"""Runner that intentionally drifts from its declared completion criteria."""

from __future__ import annotations


class NoCompletionRunner:
    def run(self, input_text: str) -> str:
        return "drift"
