# agentforge-policy-plugin

Policy guard test rig for AgentForge. Exercises `RiskLevelGuard` and `BudgetGuard`
with two deterministic agents — no LLM, no network, no flake.

## Agents

- **risky-agent** — `risk_level: high`, no `guardrails:` → `RiskLevelGuard` raises
  a blocking `error` violation.
- **budget-agent** — `max_budget_usd: 99.0` → `BudgetGuard(warning_threshold_usd=10.0)`
  raises a non-blocking `warning` violation.

## Route

`POST /api/policy-test/evaluate` — accepts `{"agent_name": "risky-agent"}` (or
`"budget-agent"`), runs `PolicyRegistry.evaluate_all()` against the loaded agent
config, returns `{"violations": [...]}`.

## Smoke tests

Located in `backend/tests/test_policy_smoke.py` in the AgentForge repo.

Install this plugin into the AgentForge environment first:

```bash
uv pip install -e /path/to/agentforge-policy-plugin
uv run pytest backend/tests/test_policy_smoke.py -v --tb=short
```
