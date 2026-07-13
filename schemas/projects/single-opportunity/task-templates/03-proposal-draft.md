---
id: T-003
kind: task
schema: single-opportunity
phase: B
risk_level: elevated
required_tools: [file_read, file_write]
depends_on: [T-002]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "Proposal draft addresses every compliance-matrix item; submission checklist built."
---
# T-003 Proposal draft
Draft the proposal/response addressing every requirement; assemble required forms/attachments; build a submission checklist. Route to operator for review.
