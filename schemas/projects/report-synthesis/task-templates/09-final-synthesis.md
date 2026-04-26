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
  - "tasks/08-completeness-audit-completion.md"
acceptance_criteria:
  - "Operator has reviewed the draft and the T-008 audit completion report and either approved or returned for changes."
  - "If approved: draft has been written to {{ deliverable_path }} and the new file's projection hash is recorded in hashes.json."
  - "OR-001 has been superseded with the new field final_synthesis: [PATH#hash] populated (or, if the schema declares final_synthesis as a field, OR is updated via supersede event)."
  - "If approved: project is archived via project.archive event, and pre-archive council members (operator-goal-aligner, source-fidelity-watcher, coverage-auditor) have emitted PASS council.report events."
  - "If returned for changes: T-007 reopens via task.status event, the operator's specific change requests are captured as a Decision artifact (synthesis_role: scope-decision), and T-007's consumes list is updated with that DEC's citation."
---

# Task T-009: Final Synthesis

## Objective

Operator reviews the draft and the T-008 audit completion report. If approved, the draft is promoted to the final `deliverable_path`. If not approved, the synthesis cycles back to drafting with operator-specific change requests captured as a typed Decision artifact.

## Step-by-Step Instructions

1. Read OR-001, the draft at `{{ deliverable_path }}.draft.md`, and the T-008 audit completion report at `tasks/08-completeness-audit-completion.md`.
2. Present the draft and the audit report to the operator. The presentation is brief:
   - Draft path (operator opens and reads).
   - Audit verdict (PASS, with one-line explanation from the T-008 report).
   - Any deferred contradictions in the open-questions section (operator may address now or accept).
3. The operator confirms one of:
   - **Approve.** Proceed to step 4.
   - **Approve with edits.** Operator specifies edits (line-level or section-level). Apply edits. If any edit affects citations (added or removed claims), re-cite — Layer 1 will reject stale or broken citations on the next state-changing event. Then proceed to step 4.
   - **Return for changes.** Operator provides specific change requests. Capture as a Decision artifact via `hw add decision < draft.md` with `synthesis_role: scope-decision`, body listing the change requests verbatim. Reopen T-007 via `hw write T-007 --status pending` and update its `consumes:` to include the new DEC citation. T-008 will re-run after T-007 produces a new draft.
4. **On approval (with or without edits):**
   - Copy the draft from `{{ deliverable_path }}.draft.md` to `{{ deliverable_path }}` (the actual final location).
   - Compute the SHA-256 of the new file's bytes; take the first 12 hex chars as the new short-hash. Record the path → short-hash mapping in `.hyperworker/hashes.json`.
   - Supersede OR-001 (or whichever OR-* is current) with a new operating-reality `add` event whose `reverses:` points at the current OR and whose `final_synthesis` field is set to `[<deliverable_path>#<final-hash>]`. The new OR carries forward all other fields unchanged. (If the schema does not declare `final_synthesis` as an OR field, declare it via `artifact-extensions.yaml` first; do not stuff the citation in a free-text note.)
5. **Pre-archive council fires.** The schema's `council.yaml` declares a `project.archive` trigger covering `operator-goal-aligner`, `source-fidelity-watcher`, and `coverage-auditor`. Run each member with context-asymmetric framing per `core/VERIFICATION.md`. Each emits a `council.report` event. Convergence rule (`all-agree-or-escalate`) decides. If any member fails, this task transitions to `blocked` with the failed council reasons; the operator decides whether to re-open T-007 or accept-with-known-gaps.
6. **Archive the project.** Append a `project.archive` event with `{project_id, completed_at, summary}` per `core/SUBSTRATE.md` §Event Kinds. The archive event causes `active_project.md` to clear; the project's projections remain in `projects/<id>/`. Archived findings are surfaced from a discovery sweep over recent task events: any `verify.layer2.fail` retries, any `task.recite` rejections — note these in the archive `summary` so the operator (or a subsequent agent) knows where to look for findings worth promoting before the next project starts.
7. Present the top-three backlog entries from `backlog.md` to the operator (read the projection at workspace root).
8. Answer @@SCAN markers from `00-REFERENCE-rules.md`.

## What the operator reviews

- **Does the synthesis serve the declared purpose?** If after reading the draft the operator cannot use it for the work it was built to inform, return for changes.
- **Are there claims that don't feel supported?** Citations should make every claim traceable. If something feels invented, audit the citation. If the citation is broken or misrepresents the source, this is a Layer 1 failure that should have been caught in T-007 — flag as a v5.x patch candidate via the friction log.
- **Are there things missing that should be there?** Sources may have been classified incorrectly (e.g., discarded when they should have been incorporated). The T-008 audit report's coverage table is the source of truth for source coverage.
- **Are there things included that shouldn't be?** Excluded topics from OR-001 should be filtered. If the operator finds out-of-scope content, return for changes with the specific topics flagged.

## What this task does NOT do

It does not produce new content. The synthesis exists; this task is the operator-review-and-finalize gate. New content emerges only if the operator returns for changes, in which case T-007 reopens.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Operator decision:** Approved | Approved-with-edits | Returned-for-changes
- **Edits applied (if any):** <count, brief description, list of citations re-validated>
- **Final deliverable path and hash:** {{ deliverable_path }}#<final-hash>
- **OR superseded with final_synthesis citation:** OR-NNN → OR-MMM (or "no — schema does not declare final_synthesis field; flagged for v5.x")
- **Pre-archive council verdicts:** operator-goal-aligner=<PASS|FAIL>, source-fidelity-watcher=<PASS|FAIL>, coverage-auditor=<PASS|FAIL>
- **Discovery sweep findings (for archive summary):** <list>
- **Failure scenarios documented (per critical risk):** 3
- **SCAN markers answered:** <count>
- **Project status:** Archived | Reopened to T-007
- **Backlog from this project:** <items the operator wants to capture for future work>
