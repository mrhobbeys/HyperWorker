---
id: T-002
kind: task
schema: lead-mining
phase: B
risk_level: elevated
required_tools: [file_read, file_write]
depends_on: [T-001]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "Exclude rules applied (vendors, newsletters/automated, internal/personal)."
  - "Duplicates merged by person and by company/domain -> one row per real lead."
  - "Excluded contacts recorded as excluded-with-reason (not silently dropped)."
---
# T-002 Filter & dedupe
Apply exclude rules; merge duplicates (same person; same company/domain). Keep current customers (flag upsell). Record exclusions with reason.
