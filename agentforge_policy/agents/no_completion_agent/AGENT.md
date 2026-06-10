---
name: no-completion-agent
namespace: project.policy-test.no-completion-agent
description: Agent whose runner output intentionally does not satisfy its declared completion_criteria.
keywords: [policy, completion, test, smoke]
model: sonnet
memory_profile: none
risk_level: low
max_budget_usd: 1.0
completion_criteria: "must-appear-in-output"
runner: agentforge_policy.agents.no_completion_agent.runner:NoCompletionRunner
scheduler: {}
---

# No-Completion Agent

Runner returns "drift" which does NOT contain the declared completion-criteria
substring. Dispatcher must surface this as a structured failure.
