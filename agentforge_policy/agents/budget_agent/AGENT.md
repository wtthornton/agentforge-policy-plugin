---
name: budget-agent
namespace: project.policy-test.budget-agent
description: High-budget test agent. Used to verify BudgetGuard raises a warning violation when max_budget_usd exceeds the threshold.
keywords: [policy, budget, test, smoke]
utterances:
  - run expensive operation
  - execute high-cost task
model: sonnet
memory_profile: none
max_budget_usd: 99.0
runner: agentforge_policy.agents.budget_agent.runner:BudgetRunner
scheduler:
  trigger: interval
  interval_seconds: 86400
---

# Budget Agent

Deterministic test fixture for the policy rig. Declares `max_budget_usd: 99.0`
so `BudgetGuard(warning_threshold_usd=10.0)` always raises a warning violation.

Exists to exercise the budget guard evaluation path without any LLM or network
dependency.
