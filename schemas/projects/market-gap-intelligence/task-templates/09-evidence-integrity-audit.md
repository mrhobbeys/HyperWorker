---
id: T-009
kind: task
schema: market-gap-intelligence
phase: D
risk_level: critical
required_tools: [file_read]
delivery_mode: constrained
depends_on: [T-008]
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "Every recommendation in the deliverable traces to a MEASURED/OBSERVED artifact by hash (or ESTIMATED on measured inputs). Orphan recommendations are listed."
  - "Every competitor cited has a found_on query (no assumed rivals leaked into the report)."
  - "Every channel-trap-owned money term has a channel-call; none recommended as a content win."
  - "≥1 disconfirming finding is present and addressed."
  - "No cross-client bleed; brand_constraints honored throughout."
  - "Full council fires and converges (or escalates to operator). Audit-only: no writes to the deliverable."
---

# Task T-009: Evidence-Integrity Audit

## Objective
Prove the recommendation rests on evidence, not fluency. Audit only — no edits to
the deliverable; failures return to T-008.

## Step-by-Step
1. Walk the deliverable. For each recommendation, resolve its citation to an
   artifact and confirm provenance is MEASURED/OBSERVED (or ESTIMATED on measured
   inputs). List orphans.
2. Confirm competitor_source_check, channel_trap_surfacing, gap_evidence,
   disconfirming_finding_present, client_scope_isolation (verification.yaml).
3. Trigger the critical-risk council. Surface a single brief summary to the
   operator, not three free-form questions.
4. The ratchet: improvements kept; regressions discard T-008's completion claim.

## Completion Report
- Acceptance criteria: <X/Y>
- Orphan recommendations: <list or none>
- Council result: <converged / escalated>
- Operator review: <required — pending/done>
