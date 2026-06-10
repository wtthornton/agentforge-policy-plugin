"""Policy plugin HTTP routes (TAP-761).

``/api/policy-test/evaluate`` keeps the pre-existing registry-level probe.
``/api/policy-demo/invoke`` exercises the full dispatcher — risk + budget +
approval + completion — with ``Response`` status codes (200 / 402 / 403 / 422)
matching the TAP-761 AC.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import BaseModel, Field

from agentforge_policy.dispatcher import invoke
from backend.policy.base import BudgetGuard, RiskLevelGuard
from backend.policy.registry import PolicyRegistry

router = APIRouter(prefix="/api/policy-test", tags=["policy-test"])
demo_router = APIRouter(prefix="/api/policy-demo", tags=["policy-demo"])


class EvaluateRequest(BaseModel):
    agent_name: str


@router.post("/evaluate")
async def evaluate(body: EvaluateRequest, request: Request) -> dict[str, Any]:
    agent_loader = getattr(request.app.state, "agent_loader", None)
    if agent_loader is None:
        raise HTTPException(status_code=500, detail="agent_loader not available")

    config = agent_loader.get(body.agent_name)
    if config is None:
        raise HTTPException(
            status_code=404, detail=f"agent '{body.agent_name}' not found"
        )

    registry = PolicyRegistry()
    registry.register_guard(RiskLevelGuard())
    registry.register_guard(BudgetGuard(warning_threshold_usd=10.0))

    violations = registry.evaluate_all(instance=MagicMock(), config=config)
    return {"violations": [v.model_dump() for v in violations]}


class InvokeRequest(BaseModel):
    agent_name: str
    prompt: str = "go"
    cost_estimate: float = Field(default=0.0, ge=0.0)
    approval_token: str | None = None


@demo_router.post("/invoke")
async def invoke_agent(
    body: InvokeRequest, request: Request, response: Response
) -> dict[str, Any]:
    agent_loader = getattr(request.app.state, "agent_loader", None)
    if agent_loader is None:
        raise HTTPException(status_code=500, detail="agent_loader not available")

    config = agent_loader.get(body.agent_name)
    if config is None:
        raise HTTPException(
            status_code=404, detail=f"agent '{body.agent_name}' not found"
        )

    # Approvals mock: `app.state.policy_approvals[agent_name] = token`.
    approvals: dict[str, str] = getattr(request.app.state, "policy_approvals", {})
    expected = approvals.get(body.agent_name)

    # Secrets mock: `app.state.policy_secrets = {"agent-name": [{"name": "key",
    # "value": "HUNT3R2"}]}`. Values are scrubbed from any denial body.
    secrets_cfg: dict[str, list[dict[str, str]]] = getattr(
        request.app.state, "policy_secrets", {}
    )
    secret_tokens = {
        entry["value"]
        for entry in secrets_cfg.get(body.agent_name, [])
        if entry.get("value")
    }

    outcome = invoke(
        config,
        prompt=body.prompt,
        cost_estimate=body.cost_estimate,
        approval_token=body.approval_token,
        expected_approval_token=expected,
        secret_tokens=secret_tokens,
    )
    response.status_code = outcome.status_code
    return outcome.body
