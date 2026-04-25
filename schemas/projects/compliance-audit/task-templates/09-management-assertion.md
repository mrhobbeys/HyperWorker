---
id: T-009
kind: task
schema: compliance-audit
phase: 3
risk_level: elevated
required_tools: [file_write]
delivery_mode: constrained
depends_on: [T-008]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-000#<short-hash>]"
acceptance_criteria:
  - "Management assertion / self-assessment authored, signed by appropriate authority."
  - "Banned tokens absent."
---

# Task T-009: Management Assertion
