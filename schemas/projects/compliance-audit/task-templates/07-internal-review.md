---
id: T-007
kind: task
schema: compliance-audit
phase: 2
risk_level: elevated
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-004, T-005, T-006]
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "Each remediated control reviewed against framework clause; gaps re-flagged as findings."
  - "Cross-cycle anti-patterns reviewed; reintroduction flagged."
---

# Task T-007: Internal Review
