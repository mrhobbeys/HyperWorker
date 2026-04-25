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
reverses: null               # or "OR-<old-id>" if a real-world change replaces a prior OR
tags: [foundation]
---

# Operating Reality OR-XXX

## Why this exists

<One paragraph: this artifact exists so council and acceptance-criteria evaluation can mechanically check whether plans assume budget, time, team capacity, or authority beyond what is actually available.>

## Notes (optional)

<Anything narrative the operator wants future agents to read when this artifact is consumed.>
