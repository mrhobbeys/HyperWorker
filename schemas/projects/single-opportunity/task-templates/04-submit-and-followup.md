---
id: T-004
kind: task
schema: single-opportunity
phase: C
risk_level: critical
required_tools: [file_read, file_write, web_fetch]
depends_on: [T-003]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "Operator approval captured BEFORE submission; submission confirmed; follow-up schedule set."
---
# T-004 Submit & follow-up
Get operator approval, then the operator submits (Claude never submits). Confirm receipt; set follow-up reminders; log Q&A/amendments.
