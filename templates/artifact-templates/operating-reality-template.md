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
# fatal_outcomes, the authority sub-block below it, operator_scope and
# reachability_map are optional v6.1.0 fields. Omit the whole set on work where
# authority is not live; declare them where it is, so agents stop asking about
# things they are already allowed to do. See core/AUTHORITY.md.
fatal_outcomes:                                   # states with no way back. Two or three, not ten.
  - "<state the engagement cannot recover from>"
authority:
  can_decide: ["<scope>", "<scope>"]
  requires_approval: ["<scope>", "<scope>"]
  green_examples:                                 # cannot end in a fatal outcome: do it, report after
    - "<representative work the agent does without asking>"
  amber_protocols:                                # the protocol IS the authorization; no per-action ask
    - action_class: "<class of change>"
      protocol:
        - "<e.g. additive first, old path removed only after the new one is proven>"
        - "<e.g. scheduled dead-man revert that does not depend on the agent running>"
        - "<e.g. one change at a time, read back after>"
      recovery_proven_by: "<citation / evidence id for the dry run>"   # null = does not authorize yet
  red_items:
    - item: "<action>"
      reason: <fatal-risk | recoverability-unknown | operator-scope>
  earned_downgrades:                              # red shrinks; each move cites what proved it
    - item: "<action>"
      from: <red | amber>
      to: <amber | green>
      proven_by: "<[KIND-NNN#hash] | evidence id | claim id>"
      at: <YYYY-MM-DD>
operator_scope:                                   # theirs because they own it, not because it is dangerous
  - "<e.g. credentials, spend, physical presence, business risk, user-visible timing>"
operator_profile: "<short label, e.g., solo-operator-modest-budget>"
reachability_map:                                 # check before referencing a doc at a party
  - party: "<agent / person / role>"
    can_reach: ["<path or resource>"]
    cannot_reach: ["<path or resource>"]
    trigger: <self-polling | human-triggered | unknown>
# soul_anchor_path is an optional v5.2.0 field pointing at the operator's filled-in
# soul.md (operator-identity anchor). null inherits soul.md at workspace root if
# one exists; otherwise the harness fires no operator_soul_anchor event. See
# core/SUBSTRATE.md §Operator Soul Anchor and SOUL.template.md / SOUL.example.md.
soul_anchor_path: <path or null>
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
