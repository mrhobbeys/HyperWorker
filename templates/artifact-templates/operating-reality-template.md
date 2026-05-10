---
id: OR-XXX
kind: operating-reality
created_at: <ISO 8601>
hash: sha256:<filled-by-harness>
budget:
  amount: <number>
  currency: <ISO 4217 code>
  frequency: <one-time | monthly | quarterly | annual>
timeline:
  hard_deadline: <YYYY-MM-DD or null>
  soft_target: <YYYY-MM-DD or null>
team:
  operator: "<name>"
  role: "<solo | lead | contributor>"
  others: []
authority:
  can_decide: ["<scope>", "<scope>"]
  requires_approval: ["<scope>", "<scope>"]
operator_profile: "<short label, e.g., solo-operator-modest-budget>"
# delegation_policy and model_selection_policy are optional v5.1 fields. Omit
# either to inherit harness defaults; set to capture preferences once at
# bootstrap so they propagate across sessions instead of being re-prompted.
delegation_policy:
  mode: <step-by-step | run-to-completion | hybrid>            # how the agent engages
  execution_mode: <interactive | agent | observer>             # v5.2.0 — pause-batching preference; default interactive
  subagent_use: <never | when-helpful | aggressive>            # subagent dispatch posture
  pause_on:
    - council-failures                                          # any council.escalated event
    - layer1-failures-after-N-retries                           # N from active model profile retry_budget
    - operator-mid-flow-directives                              # decision.add with actor: operator
    - phase-boundaries                                          # task.complete on phase-final task
    - critical-risk-task-completion                             # task.complete with risk_level: critical
  resume_authority: <operator-only | agent-judgment | both>     # who may unblock after a pause
model_selection_policy:
  prefer: <cheapest-capable | fastest-capable | most-capable | manual-only>
  fallback_trigger: <layer1-failure-after-N | layer2-failure | council-non-convergence | never>
  fallback_target: "<explicit model profile_id, e.g., claude-opus-4-7>"  # null if fallback_trigger: never
  per_task_overrides:
    - task_kind: "<task-kind label>"
      prefer: <cheapest-capable | fastest-capable | most-capable>
reverses: null               # or "OR-<old-id>" if a real-world change replaces a prior OR
tags: [foundation]
---

# Operating Reality OR-XXX

## Why this exists

<One paragraph: this artifact exists so council and acceptance-criteria evaluation can mechanically check whether plans assume budget, time, team capacity, or authority beyond what is actually available.>

## Notes (optional)

<Anything narrative the operator wants future agents to read when this artifact is consumed.>
