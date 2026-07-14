---
id: T-006
kind: task
schema: program
phase: C
risk_level: critical
required_tools: [file_read, file_write, hash_compute]
delivery_mode: constrained
depends_on: [T-004]
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "This cycle's roll-up Finding (T-004) is complete at Layer 2 before this task starts."
  - "The operator reviewed the roll-up's promote_recommendations and retire_recommendations — each was actioned (routed to T-003/T-005), explicitly deferred, or explicitly declined; none left silently unaddressed."
  - "If OR-001.lifecycle == ongoing: hw cycle close was run — next_due computed as closed_at + cadence_days and recorded on the cycle.close event; CYCLES.md and active_project.md re-rendered; this cycle's recurring_tasks (T-004, T-006) reset to pending for the next cycle."
  - "If OR-001.lifecycle == terminal and the operator declares the program goal itself finished: hw wrap runs instead of hw cycle close, per core/LOCK.md — a program with an open cycle cannot wrap."
---

# Task T-006: Program Review (recurring — cycle close + operator review)

## Objective

Close the program's current cycle: present the roll-up to the operator, resolve its
recommendations, compute `next_due`, and reset the cycle's recurring tasks. This is
the other half of the schema's `recurring_tasks:` pair with T-004.

## Step-by-Step Instructions

1. Confirm T-004 (roll-up cycle) completed at Layer 2 for this cycle.
2. Present the roll-up Finding to the operator: workstream statuses, overdue
   workstreams, promote/retire recommendations.
3. For each `promote_recommendations` entry: operator decides act now (branch
   T-003), defer (note in this task's completion report, revisit next cycle), or
   decline (note reason — this is not silence, it is a recorded call).
4. For each `retire_recommendations` entry: same three-way disposition, routing
   accepted ones to a T-005 branch.
5. If `OR-001.lifecycle == ongoing`: confirm this cycle's task set
   (`recurring_tasks:` — T-004 and this task) is `complete` at Layer 2. Compute
   `next_due = closed_at + cadence_days`. Append `cycle.close` with `{cycle_id,
   closed_at, summary, next_due}`. Re-render `CYCLES.md` and `active_project.md`
   (`Next due:` line updates; the pointer stays on this project — it does not
   archive). Reset T-004 and this task (T-006) to `pending` for the next cycle.
6. If `OR-001.lifecycle == terminal` and every workstream has reached a terminal
   status (`retired` or `done`) and the operator declares the program goal itself
   finished: run `hw wrap` instead (discovery sweep, `project.archive`,
   present top-3 backlog) — not valid while any cycle is open.
7. Answer @@SCAN markers.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Cycle closed:** C-NNN, next_due: <date> (ongoing) / N/A (terminal, not yet wrapped)
- **Promote recommendations actioned:** <list — acted / deferred / declined, with which>
- **Retire recommendations actioned:** <list — acted / deferred / declined, with which>
- **Outputs produced:** cycle.close EV-NNNN (or project.archive EV-NNNN if
  wrapping); updated CYCLES.md / active_project.md
- **Recurring tasks reset:** T-004, T-006 -> pending (ongoing case only)
- **Discoveries:** <e.g., "operator declined every promote recommendation this cycle — promote_criteria may be miscalibrated, worth an OR-001 supersede">
- **Recommended follow-up:** "hw next-step will select the next pending task (T-004 for the new cycle, or a T-002/T-003/T-005 branch if the operator has one queued)."
