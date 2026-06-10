"""Deterministic invoke-dispatcher for the policy rig (TAP-761).

Runs an agent's runner through a synthetic guard chain:

1. :class:`RiskLevelGuard` — if it raises a blocking error AND the request
   does not carry a matching approval token, return HTTP 403.
2. :class:`BudgetGuard` — if the caller-declared ``cost_estimate`` exceeds
   ``max_budget_usd``, return HTTP 402 with a cost breakdown.
3. Runner — call ``runner.run(input)`` deterministically.
4. Completion — if ``config.completion_criteria`` is non-empty and not a
   substring of the runner output, return a 422 structured failure.

All error bodies are scrubbed against a caller-supplied ``secret_tokens`` set
so a leaked SecretStr / api key cannot end up in a denial response.
"""

from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock

from backend.models.agent_config import AgentConfig
from backend.policy.base import BudgetGuard, PolicyViolation, RiskLevelGuard
from backend.policy.registry import PolicyRegistry

logger = logging.getLogger(__name__)


@dataclass
class DispatchOutcome:
    status_code: int
    body: dict[str, Any]


def _scrub_body(body: dict[str, Any], secrets: set[str]) -> dict[str, Any]:
    """Return a copy of ``body`` with any secret substring replaced by ``<redacted>``.

    Walks dict / list / str recursively. Non-string leaves are passed through.
    """

    def _walk(value: Any) -> Any:
        if isinstance(value, str):
            out = value
            for s in secrets:
                if s and s in out:
                    out = out.replace(s, "<redacted>")
            return out
        if isinstance(value, dict):
            return {k: _walk(v) for k, v in value.items()}
        if isinstance(value, list):
            return [_walk(v) for v in value]
        return value

    result = _walk(body)
    assert isinstance(result, dict)
    return result


def _load_runner(spec: str) -> Any:
    """Resolve ``module.path:ClassName`` → instance, mirroring AgentLoader runner resolution."""
    if ":" not in spec:
        raise ValueError(f"runner spec must be 'module:Class', got {spec!r}")
    mod_path, class_name = spec.split(":", 1)
    module = importlib.import_module(mod_path)
    cls = getattr(module, class_name)
    return cls()


def _evaluate_guards(
    config: AgentConfig, cost_estimate: float
) -> list[PolicyViolation]:
    """Run the two canonical guards (risk + budget) against *config*.

    Registry receives a ``MagicMock`` ``instance`` since guards only consult
    the config in the current implementation.
    """
    registry = PolicyRegistry()
    registry.register_guard(RiskLevelGuard())
    registry.register_guard(BudgetGuard(warning_threshold_usd=max(cost_estimate, 10.0)))
    return list(registry.evaluate_all(instance=MagicMock(), config=config))


def invoke(
    config: AgentConfig,
    *,
    prompt: str = "go",
    cost_estimate: float = 0.0,
    approval_token: str | None = None,
    expected_approval_token: str | None = None,
    secret_tokens: set[str] | None = None,
) -> DispatchOutcome:
    """Run the full guard → runner → completion pipeline.

    Args:
        config: the agent to dispatch.
        prompt: forwarded to ``runner.run``.
        cost_estimate: caller-declared cost in USD, compared to
            ``config.max_budget_usd`` for the 402 path.
        approval_token: token the caller has presented (None = no approval).
        expected_approval_token: when non-None, an ``approval_token`` that
            matches unlocks otherwise-blocking risk violations.
        secret_tokens: strings to scrub from any denial response body.
    """
    secrets = secret_tokens or set()

    violations = _evaluate_guards(config, cost_estimate)
    blocking = [v for v in violations if v.severity == "error"]

    if blocking:
        approved = (
            expected_approval_token is not None
            and approval_token == expected_approval_token
        )
        if not approved:
            body = {
                "denied": True,
                "reason": "blocking-violations",
                "violations": [v.model_dump() for v in blocking],
                "agent": config.name,
            }
            return DispatchOutcome(403, _scrub_body(body, secrets))
        logger.info("policy-demo: high-risk agent %s approved via token", config.name)

    if cost_estimate > config.max_budget_usd:
        body = {
            "denied": True,
            "reason": "budget-exceeded",
            "agent": config.name,
            "cost_breakdown": {
                "estimate_usd": cost_estimate,
                "budget_usd": config.max_budget_usd,
                "overrun_usd": round(cost_estimate - config.max_budget_usd, 4),
            },
        }
        return DispatchOutcome(402, _scrub_body(body, secrets))

    runner = _load_runner(config.runner) if config.runner else None
    output = runner.run(prompt) if runner is not None else ""

    if config.completion_criteria and config.completion_criteria not in output:
        body = {
            "denied": True,
            "reason": "completion-criteria-unmet",
            "agent": config.name,
            "expected_substring": config.completion_criteria,
            "actual_output": output,
        }
        return DispatchOutcome(422, _scrub_body(body, secrets))

    # Informational: warnings (non-blocking) are surfaced alongside success
    # so callers can observe BudgetGuard's non-blocking signal.
    warnings = [v.model_dump() for v in violations if v.severity == "warning"]

    return DispatchOutcome(
        200,
        {
            "ok": True,
            "agent": config.name,
            "output": output,
            "warnings": warnings,
        },
    )
