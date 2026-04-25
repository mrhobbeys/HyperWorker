---
id: T-002
kind: task
schema: compliance-audit
phase: 1
risk_level: elevated
required_tools: [file_write, file_read]
delivery_mode: constrained
depends_on: [T-001]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-000#<short-hash>]"
acceptance_criteria:
  - "Each control mapped is rated: implemented / partial / missing."
  - "Each non-implemented control has a finding (F-XXX) capturing the gap."
  - "Findings tagged with framework_clause."
---

# Task T-002: Gap Assessment
