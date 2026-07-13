---
id: T-003
kind: task
schema: lead-mining
phase: C
risk_level: standard
required_tools: [file_read, file_write, web_search, web_fetch]
depends_on: [T-002]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "Each lead has company, role (best effort), and what their business does."
  - "Each lead has an inferred NEED captured from the original email content."
---
# T-003 Enrich & infer need
For each lead: add company/role/what-they-do (web enrich as needed) and the inferred need from their original email (what service/interest they reached out about). Mark unconfirmed where unsure.
