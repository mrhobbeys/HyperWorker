---
id: T-001
kind: task
schema: compliance-audit
phase: 1
risk_level: elevated
required_tools: [file_write, file_read]
delivery_mode: constrained
depends_on: [T-000]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-000#<short-hash>]"
acceptance_criteria:
  - "Every framework clause in scope mapped to an existing or planned control."
  - "Mapping document (controls-matrix.md) authored."
---

# Task T-001: Control Mapping
