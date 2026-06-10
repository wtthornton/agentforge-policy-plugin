---
name: low-risk-agent
namespace: project.policy-test.low-risk-agent
description: Low-risk test agent. Used to verify the policy dispatcher clears invocations with no blocking violation.
keywords: [policy, low-risk, test, smoke]
model: sonnet
memory_profile: none
risk_level: low
max_budget_usd: 1.0
completion_criteria: "ok"
runner: agentforge_policy.agents.low_risk_agent.runner:LowRiskRunner
scheduler: {}
---

# Low-Risk Agent

Returns "invoke:ok" deterministically so the completion-criteria probe
(substring "ok") matches on happy paths.
