---
name: risky-agent
namespace: project.policy-test.risky-agent
description: High-risk test agent with no guardrails. Used to verify RiskLevelGuard raises a blocking violation.
keywords: [policy, risk, test, smoke]
utterances:
  - run risky operation
  - execute dangerous task
model: sonnet
memory_profile: none
risk_level: high
runner: agentforge_policy.agents.risky_agent.runner:RiskyRunner
---

# Risky Agent

Deterministic test fixture for the policy rig. Declares `risk_level: high` with
no `guardrails:` key so `RiskLevelGuard` always raises a blocking error violation.

Exists to exercise the policy guard evaluation path without any LLM or network
dependency.
