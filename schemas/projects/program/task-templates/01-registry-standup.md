---
id: T-001
kind: task
schema: program
phase: A
phase_step: 2
risk_level: standard
required_tools: [file_read, file_write, hash_compute]
delivery_mode: constrained
depends_on: [T-000]
consumes:
  - "[OR-001#<short-hash>]"
  - "[WS-*#<short-hash>]"
acceptance_criteria:
  - "The registry projection (projects/<id>/workstreams/) contains one rendered file per current (non-superseded) workstream artifact, matching T-000's registrations exactly."
  - "If OR-001.lifecycle == ongoing, a cycle.open event is emitted with the recorded cadence, opening the program's first cycle."
  - "If OR-001.lifecycle == ongoing, CYCLES.md exists (even if empty of closed cycles) and active_project.md carries a Next due: line once cadence_days is computed."
  - "Every registered workstream's status is one of the legal enum values and matches its origin instance's actual observed status from T-000."
---

# Task T-001: Registry Standup

## Objective

Stand up the workstream registry projection and, if this program is
`lifecycle: ongoing`, open its first cycle. This is the last Phase A task; after it
the program is in steady state (Phase B repeatable procedures, Phase C recurring
cycle tasks).

## Step-by-Step Instructions

1. Read OR-001 and every `WS-NNN` artifact T-000 registered.
2. Render the registry projection: one file per current workstream, plus an
   index/summary view listing `child_project_id`, `status`, `lifecycle`,
   `instance_path` for every entry at a glance.
3. If `OR-001.lifecycle == ongoing`: emit `cycle.open` with `{project_id, cycle_id: C-001, opened_at, cadence: OR-001.rollup_cadence}`. Compute `cadence_days` once
   (this run only — subsequent cycles reuse it).
4. Render `CYCLES.md` (empty of closed cycles at this point) and update
   `active_project.md` with `Next due:` once `cadence_days` is known.
5. If `OR-001.lifecycle == terminal`, skip step 3-4; note in the completion report
   that this program has a defined end rather than a cycle cadence.
6. Answer @@SCAN markers.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…]; [WS-001#…] through [WS-NNN#…]
- **SCAN markers answered:** <count>
- **Outputs produced:** registry projection files; cycle.open EV-NNNN (if ongoing);
  CYCLES.md; updated active_project.md
- **Registered workstream count:** <N> (<active> active, <parked> parked)
- **Discoveries:** <e.g., "one existing instance registered by T-000 is itself lifecycle: ongoing and already overdue on its own cadence — flagged for the first roll-up">
- **Recommended follow-up:** "Program is in steady state. Operator may initiate a spawn (T-002) or the first roll-up cycle (T-004) is due <date>."
