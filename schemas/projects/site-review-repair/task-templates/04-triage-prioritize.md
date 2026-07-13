---
id: T-004
kind: task
schema: site-review-repair
phase: 2
risk_level: elevated
task_kind: triage
delivery_mode: constrained
depends_on: [T-002,T-003]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "All findings ranked by severity x effort into a fix order (DEC)."
  - "Blockers separated from low-priority polish."
---

# Task T-004: Triage & Prioritize

Rank everything from the audits into a concrete fix order. Capture the ranking as a Decision.
