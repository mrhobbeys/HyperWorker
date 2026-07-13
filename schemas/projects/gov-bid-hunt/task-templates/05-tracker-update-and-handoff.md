---
id: T-005
kind: task
schema: gov-bid-hunt
phase: C
risk_level: standard
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-004]
acceptance_criteria:
  - "This segment's tab in the shared tracker is updated with current statuses + new finds."
  - "A scope.complete snapshot + session.handoff are written for clean re-entry."
  - "Next sweep date is set per cadence."
---

# Task T-005: Tracker Update + Handoff
1. Update this segment's tab in the tracker at OR-001 deliverable_path.
2. Emit scope.complete covering PROJECT.md §Scope items, then session.handoff (last/next task, open questions, recommended first action, next sweep date).
3. Report status up to the orchestrator/parent program, if this segment runs under one.

## Completion Report
- Tracker updated: <yes>
- Next sweep: <date>
- Handoff written: <yes>
