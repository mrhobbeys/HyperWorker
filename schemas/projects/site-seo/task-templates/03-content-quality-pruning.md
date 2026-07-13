---
id: T-003
kind: task
schema: site-seo
phase: 3
risk_level: elevated
task_kind: content-plan
delivery_mode: constrained
depends_on: [T-002]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "Thin/low-value posts identified with prune / consolidate / improve recommendations (helpful-content)."
  - "Each recommended change marked executor (operator/dev) with rollback; no live change by the worker."
  - "SERVER-HANDOFF/dev-handoff produced for the changes."
---

# Task T-003: Content Quality & Pruning

Identify thin/low-value content and recommend prune/consolidate/improve. Propose only; hand changes to operator/dev with rollback.
