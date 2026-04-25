---
id: T-008
kind: task
schema: compliance-audit
phase: 3
risk_level: critical
required_tools: [file_read, file_write]
delivery_mode: prescribed
depends_on: [T-007]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-000#<short-hash>]"
acceptance_criteria:
  - "Evidence package indexed by control / framework clause."
  - "File-naming follows Tier 4 DOCUMENTATION convention."
  - "Each item resolves to a real evidence file with timestamp inside audit period."
---

# Task T-008: Evidence Package Assembly  *(critical)*
