---
id: T-009
kind: task
schema: report-synthesis
phase: D
risk_level: critical
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-008]
consumes:
  - "[OR-001#<short-hash>]"
  - "Draft at {{ deliverable_path }}.draft.md"
  - "audit-report-T008.md"
acceptance_criteria:
  - "Operator has reviewed the draft and audit report and approved (or returned for changes)."
  - "If approved, draft is written to {{ deliverable_path }}."
  - "Final write event in events.jsonl is captured (deliverable.finalize event)."
  - "If returned, T-007 reopens with operator's specific change requests."
---

# Task T-009: Final Synthesis

## Objective

Operator reviews the draft and audit report. If approved, the draft is promoted to the final deliverable_path. If not approved, the synthesis cycles back to drafting with operator-specific change requests.

## Step-by-Step Instructions

1. Read OR-001, the draft, and the T-008 audit report.
2. Present the draft and audit report to the operator. The presentation should be brief:
   - Draft path (operator opens and reads).
   - Audit verdict (PASS, with one-line explanation).
   - Any deferred contradictions in the open-questions section (operator may address now or accept).
3. The operator confirms one of:
   - **Approve.** Proceed to step 4.
   - **Approve with edits.** Operator specifies edits (line-level or section-level). Apply edits, re-cite if changes affect citations, then proceed to step 4.
   - **Return for changes.** Operator provides specific change requests. Capture as a Decision artifact (`synthesis_role: scope-decision`), reopen T-007 with the new constraints. T-008 audit re-runs.
4. On approval (with or without edits):
   - Copy draft to `{{ deliverable_path }}` (the actual final location).
   - Emit `deliverable.finalize` event with the final hash.
   - Update OR-001 with `final_synthesis: [PATH#hash]`.
5. Council fires (project archive trigger). `source-fidelity-watcher`, `coverage-auditor`, `operator-goal-aligner` confirm pre-archive.
6. Run `hw wrap` to initiate closure protocol: discovery sweep, archive, present backlog.
7. Answer @@SCAN markers.

## What the operator reviews

- **Does the synthesis serve the declared purpose?** If after reading the draft, the operator cannot use it for the work it was built to inform, return for changes.
- **Are there claims that don't feel supported?** Citations should make every claim traceable. If something feels invented, audit the citation. If the citation is broken or misrepresents the source, this is a Layer 1 failure that should have been caught — flag as a v5.x patch candidate.
- **Are there things missing that should be there?** Sources may have been classified incorrectly (e.g., discarded when they should have been incorporated). The audit report's coverage table makes this auditable.
- **Are there things included that shouldn't be?** Excluded topics from OR-001 should be filtered. If the operator finds out-of-scope content, return for changes with the specific topics flagged.

## What this task does NOT do

It does not produce new content. The synthesis exists; this task is the operator-review-and-finalize gate. New content emerges only if the operator returns for changes, in which case T-007 reopens.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Operator decision:** Approved | Approved-with-edits | Returned-for-changes
- **Edits applied (if any):** <count, brief description>
- **Final deliverable path and hash:** {{ deliverable_path }}#<final-hash>
- **OR-001 updated with final_synthesis citation:** yes/no
- **Council verdicts at archive:** <one line each>
- **Failure scenarios documented (per critical risk):** 3
- **SCAN markers answered:** <count>
- **Project status:** Archived | Reopened to T-007
- **Backlog from this project:** <items the operator wants to capture for future work>
