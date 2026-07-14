---
id: T-004
kind: task
schema: program
phase: C
risk_level: elevated
required_tools: [file_read, file_write, hash_compute]
delivery_mode: constrained
depends_on: [T-001]
consumes:
  - "[OR-001#<short-hash>]"
  - "[WS-*#<short-hash>]"
acceptance_criteria:
  - "Every workstream with status active or parked was read this cycle — SESSION-HANDOFF.md or CYCLES.md, READ-ONLY — and appears in workstreams_covered on the roll-up Finding."
  - "Every workstream's last_rollup_citation is updated to this cycle's citation (path + sha256 + cycle_id + checked_at)."
  - "Every workstream that is itself lifecycle: ongoing and OVERDUE per its own CYCLES.md (core/LOCK.md §Ongoing Projects) appears in overdue_workstreams."
  - "promote_recommendations and retire_recommendations are populated (possibly empty lists, never omitted) with the reasoning in the Finding body."
  - "No sibling instance's events.jsonl was opened as a writer at any point in this task."
---

# Task T-004: Roll-Up Cycle (recurring)

## Objective

Read every registered workstream's projections read-only and record one roll-up
Finding for this program cycle: statuses, blockers, overdue cycles, promote/retire
recommendations. This is one of the schema's `recurring_tasks:` — `hw cycle close`
(T-006) resets it to `pending` for the next cycle.

## Step-by-Step Instructions

1. Read OR-001 and the current registry (every non-superseded `WS-NNN`).
2. For each workstream with `status: active` or `status: parked`:
   - Read `<instance_path>/projects/<child_project_id>/SESSION-HANDOFF.md` and, if
     the workstream is itself `lifecycle: ongoing`, `CYCLES.md`. Read-only.
   - Compute the SHA-256 of the file read; record the citation per
     `00-REFERENCE-rules.md` §Cross-Instance Citation Format.
   - Note current status, any open blockers mentioned in the handoff, and — for
     ongoing sibling workstreams — whether `next_due` has passed with no new
     `cycle.open` (OVERDUE, per `core/LOCK.md` §Ongoing Projects).
   - Consider fanning out one read-only sub-pass per workstream (delegation
     recommended per `capability-gates.yaml`); converge on a single roll-up
     Finding as the one serial writer (`core/SUBSTRATE.md` §Single-Writer Rule —
     parallel actors write drafts, one writer appends).
3. Cross-check each workstream's read state against `OR-001.promote_criteria`:
   flag any that plausibly meet it for `promote_recommendations` (a
   recommendation here is not a promotion — T-003 still runs the full
   spawn-pause protocol).
4. Flag any workstream that has produced nothing new across N consecutive cycles,
   or whose own instance is archived/abandoned, for `retire_recommendations`.
5. Update each covered workstream's `last_rollup_citation` (a `workstream.add`
   with `reverses:` unset — this is metadata refresh, not a status change; if a
   status change is ALSO warranted, that is a separate supersede event with its
   own rationale, not folded into the citation refresh).
6. Write the roll-up Finding: `rollup_role: rollup`, `cycle_id`,
   `workstreams_covered`, `overdue_workstreams`, `promote_recommendations`,
   `retire_recommendations`, with reasoning in the body.
7. Answer @@SCAN markers.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…]; [WS-001#…] through [WS-NNN#…]
- **SCAN markers answered:** <count>
- **Outputs produced:** roll-up Finding F-NNN; updated last_rollup_citation on
  <N> workstreams
- **Workstreams covered:** <N>/<total active+parked>
- **Overdue workstreams:** <list or "none">
- **Promote recommendations:** <list with one-line reason each, or "none">
- **Retire recommendations:** <list with one-line reason each, or "none">
- **Broken citations found:** <list — a sibling projection path that no longer resolves — or "none">
- **Discoveries:** <e.g., "workstream WS-004 has had an identical SESSION-HANDOFF.md for 3 cycles running — likely stalled, not just idle">
- **Recommended follow-up:** "Operator reviews recommendations at T-006 program review."
