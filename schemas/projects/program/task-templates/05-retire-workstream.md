---
id: T-005
kind: task
schema: program
phase: B
risk_level: critical
required_tools: [file_read, file_write, hash_compute]
delivery_mode: constrained
depends_on: [T-001]
consumes:
  - "[OR-001#<short-hash>]"
  - "[WS-*#<short-hash>]"
acceptance_criteria:
  - "A retire Decision (synthesis_role: retire-decision) is recorded, citing the workstream and the concrete reason (item fully graduated via promotion, work abandoned, sibling instance archived, or operator call)."
  - "The workstream's status is superseded to retired via a new workstream.add with reverses: <current WS-NNN> — never an in-place edit."
  - "If retirement follows a promotion, the new workstream's promoted_from already points back here; this task does not duplicate that citation."
  - "Operator review completed before the retire Decision is recorded (critical risk)."
---

# Task T-005: Retire Workstream (repeatable)

## Objective

Formally retire a workstream once its work is done, abandoned, or fully absorbed by
a promotion. Run each retirement as a branch of this task
(`hw branch T-005 <child_project_id>`).

## Step-by-Step Instructions

1. Identify the workstream to retire and the concrete reason: `promoted` (its hot
   item already graduated and nothing else in it is active), `done` (its own
   instance reached `project.archive` with nothing further expected — use
   `status: done` instead of `retired` in this case, see note below), or
   operator-declared abandonment.
2. Confirm with the operator before recording the Decision — this is critical
   risk (`verification.yaml`).
3. Record a Decision (`synthesis_role: retire-decision`, `cites_workstream:
   [<current WS-NNN#hash>]`, rationale stating the concrete reason).
4. Register the status change: `hw add workstream` with `reverses: <current
   WS-NNN>` and `status: retired` (or `status: done` if the sibling instance
   itself archived cleanly — see `artifact-extensions.yaml` workstream.status for
   the distinction). All other fields carry forward unchanged except `tags` if
   updated.
5. Answer @@SCAN markers.

## Note on `retired` vs `done`

`retired` means this program stops tracking the workstream (the item may still be
someone's problem, just not this program's). `done` means the sibling instance's own
project completed cleanly (`project.archive`) with nothing further expected. Both are
terminal for this registry; the distinction is for the roll-up's own record-keeping,
not a behavioral difference in this task.

## Completion Report (filled by executor, per invocation)

- **Acceptance criteria:** <X/Y pass>
- **Workstream retired:** [WS-NNN#…] -> [WS-NNN#… (new)]
- **Reason:** <concrete reason>
- **Terminal status:** retired / done
- **Outputs produced:** DEC-NNN (retire-decision); new WS-NNN (superseding entry)
- **Discoveries:** <e.g., "this workstream never produced a promote-worthy item across its whole run — candidate anti-pattern for the routing rule that spawned it">
- **Recommended follow-up:** "none" / "Write AP-NNN capturing the routing-rule pattern that led here."
