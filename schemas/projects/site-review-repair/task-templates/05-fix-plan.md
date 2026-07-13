---
id: T-005
kind: task
schema: site-review-repair
phase: 2
risk_level: elevated
task_kind: fix-plan
delivery_mode: constrained
depends_on: [T-004]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "Each proposed change written as a draft with target URL/file, the change, and a rollback."
  - "Plan presented to operator; approval recorded as a DEC before any implementation."
---

# Task T-005: Fix Plan (operator-approved)

Draft the fixes for operator approval. Nothing is implemented until the operator approves (Tier 1).
