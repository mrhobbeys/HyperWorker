---
id: T-006
kind: task
schema: compliance-audit
phase: 2
risk_level: critical
required_tools: [file_read, file_write, http_fetch]
delivery_mode: prescribed
depends_on: [T-001]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-000#<short-hash>]"
acceptance_criteria:
  - "Each in-scope control has supporting evidence files."
  - "All evidence is system-generated (not screenshot)."
  - "Each evidence file is from production within OR-001.audit_period."
  - "Banned tokens (approximately, should be, we believe) absent from any evidence narrative."
---

# Task T-006: Evidence Gathering  *(critical — fabricated evidence is a Tier 1 violation)*

This is the highest-stakes task in the audit. Council fires; layer-2 banned-token scan and evidence-traceability checks run.
