---
id: T-006
kind: task
schema: site-review-repair
phase: 3
risk_level: critical
task_kind: implement
delivery_mode: constrained
depends_on: [T-005]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "Only operator-approved changes applied; each with a backup/rollback."
  - "No destructive or bulk action without explicit approval."
  - "Each change logged as a DEC with change_type and rollback_ref."
---

# Task T-006: Implement Approved Fixes

Apply ONLY approved fixes. Back up before editing. Record change_type + rollback for each (critical; operator review required).
