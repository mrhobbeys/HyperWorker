---
id: T-004
kind: task
schema: opportunity-hunt
phase: C
risk_level: critical
required_tools: [file_read, file_write, web_fetch]
delivery_mode: constrained
depends_on: [T-002, T-003]
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "The top opportunity's deadline + requirements are RE-VERIFIED live before any drafting."
  - "A pursue/skip Decision is recorded with rationale and eligibility confirmation."
  - "If pursuing: a draft outreach/proposal/application + submission checklist exists. If skipping: the reason is recorded."
  - "Operator approval captured before anything is actually sent or submitted."
---

# Task T-004: Pursue/Skip Decision + Draft
1. Re-verify the top opportunity live (deadline/window, eligibility requirements, submission method).
2. Confirm eligibility (or teaming plan). If blocked (e.g., partner enrollment pending), record what must clear first.
3. Record a pursue/skip Decision.
4. If pursuing: draft the outreach/proposal/application + a submission checklist; route to operator for approval. Never send or submit without operator approval.

## Completion Report
- Decision: <DEC-NNN pursue/skip>
- Draft/checklist path: <file>
- Operator approval: <pending/given>
