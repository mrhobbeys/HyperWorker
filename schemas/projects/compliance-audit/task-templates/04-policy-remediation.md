---
id: T-004
kind: task
schema: compliance-audit
phase: 2
risk_level: elevated
required_tools: [file_write]
delivery_mode: constrained
depends_on: [T-003]
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "Each policy gap addressed with revised or new policy text."
  - "Policy frequency (e.g., quarterly access review) matches evidence frequency."
  - "Revision history captured per Tier 4 DOCUMENTATION."
---

# Task T-004: Policy Remediation
