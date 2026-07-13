---
id: T-004
kind: task
schema: gov-bid-hunt
phase: C
risk_level: critical
required_tools: [file_read, file_write, web_fetch]
delivery_mode: constrained
depends_on: [T-002, T-003]
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "The top opportunity's deadline + requirements are RE-VERIFIED live before any drafting."
  - "A bid/no-bid Decision is recorded with rationale and eligibility confirmation."
  - "If bidding: a draft response / submission checklist exists. If no-bid: the reason is recorded."
  - "Operator approval captured before any actual submission."
---

# Task T-004: Bid/No-Bid + Draft
1. Re-verify the top opportunity live (deadline, set-aside, requirements, submission method).
2. Confirm eligibility (or teaming plan). If blocked (e.g., SAM.gov), record what must clear first.
3. Record a bid/no-bid Decision.
4. If bidding: draft the response + a submission checklist; route to operator for approval. Never submit without operator approval.

## Completion Report
- Decision: <DEC-NNN bid/no-bid>
- Draft/checklist path: <file>
- Operator approval: <pending/given>
