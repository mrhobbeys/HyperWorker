---
id: T-000
kind: task
schema: compliance-audit
phase: 1
risk_level: elevated
required_tools: [file_write, file_read]
delivery_mode: constrained
depends_on: []
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "Audit scope confirmed in writing with auditor (email or signed scope memo)."
  - "Scope captured as DEC-000 with framework_clause references."
  - "Prior-audit findings (if any) imported as findings with from_prior_audit: true."
---

# Task T-000: Scope Confirmation

Confirm scope with auditor. The most common failure: scope drift mid-cycle. Lock it now.
