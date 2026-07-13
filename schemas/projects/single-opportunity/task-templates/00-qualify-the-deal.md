---
id: T-000
kind: task
schema: single-opportunity
phase: A
risk_level: standard
required_tools: [file_read, file_write, web_fetch]
depends_on: []
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "Deadline + requirements re-verified live; bid/no-bid recommendation with rationale + eligibility check."
---
# T-000 Qualify the deal
Re-verify the opportunity live (deadline, requirements, set-aside/eligibility, submission method, value). Record a go/no-go recommendation. If gated (SAM/cert/membership/teaming), state what must clear first.
