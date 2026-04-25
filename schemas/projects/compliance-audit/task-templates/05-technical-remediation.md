---
id: T-005
kind: task
schema: compliance-audit
phase: 2
risk_level: critical
required_tools: [admin_console, code_lint, file_write]
delivery_mode: prescribed
depends_on: [T-003]
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "Each technical gap remediated in production (not staging)."
  - "Remediation captured as DEC-XXX with framework_clause."
  - "Rollback plan recorded for each change."
---

# Task T-005: Technical Remediation  *(critical)*
