---
id: T-010
kind: task
schema: compliance-audit
phase: 3
risk_level: elevated
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-008, T-009]
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "Walkthrough simulates auditor questions for each in-scope control."
  - "Gaps surfaced during walkthrough re-opened as blocked status on T-005 / T-006."
---

# Task T-010: Mock Audit Walkthrough
