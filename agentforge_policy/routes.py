"""Policy test plugin HTTP routes — POST /api/policy-test/evaluate."""

from __future__ import annotations

from unittest.mock import MagicMock

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from backend.policy.base import BudgetGuard, RiskLevelGuard
from backend.policy.registry import PolicyRegistry

router = APIRouter(prefix="/api/policy-test", tags=["policy-test"])


class EvaluateRequest(BaseModel):
    agent_name: str


@router.post("/evaluate")
async def evaluate(body: EvaluateRequest, request: Request) -> dict:
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
