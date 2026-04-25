---
id: T-011
kind: task
schema: compliance-audit
phase: 3
risk_level: critical
required_tools: [file_read, file_write]
delivery_mode: prescribed
depends_on: [T-009, T-010]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-000#<short-hash>]"
acceptance_criteria:
  - "Pre-submission council passes (regulator-perspective + scope-guard + evidence-traceability + prior-finding + cross-cycle)."
  - "Final package transmitted to auditor via OR-001.auditor_contact channel."
  - "Submission tracking / receipt captured."
---

# Task T-011: Final Submission  *(critical)*

Pre-submission council fires automatically (`pre.submission` trigger). Final submission proceeds only on `council.converged`.
