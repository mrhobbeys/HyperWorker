---
id: T-003
kind: task
schema: compliance-audit
phase: 1
risk_level: standard
required_tools: [file_write]
delivery_mode: constrained
depends_on: [T-002]
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "Gaps ranked by severity (auditor-failing) and remediation effort."
  - "Remediation plan captured as DEC-XXX with target completion before audit_period.end."
---

# Task T-003: Prioritize Gaps
