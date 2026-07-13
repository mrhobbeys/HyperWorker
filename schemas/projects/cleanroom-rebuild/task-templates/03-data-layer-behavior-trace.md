---
id: T-003
kind: task
schema: cleanroom-rebuild
phase: B
risk_level: standard
required_tools: [file_write, app_driver, sql_trace, sql_query]
delivery_mode: constrained
depends_on: [T-001]
consumes:
  - "[OR-001#<short-hash>]"
  - "[OBS-NNN#<short-hash>]"  # the screen OBS / action whose data effect this branch traces
acceptance_criteria:
  - "For each in-scope user action, a SQL Server trace + DB before/after diff is captured as OBS (observation_type: sql-trace and/or db-diff) with capture_method: sql-trace | db-diff and source_ref = the action name."
  - "Each trace OBS records the exact statements issued and the row-level before/after delta — a BLACK-BOX measurement of what the action does to data (no code reading)."
  - "Every OBS carries source=original, zone=observed, consumable_by_build=false; this task writes only to observed/."
  - "Actions whose data effect is ambiguous (e.g., depends on hidden state) are flagged in the completion report for repeated measurement."
  - "Zero Tier 1 violations from 00-REFERENCE-rules."
---

# Task T-003: Data-Layer Behavior Trace

## Objective

For each user action, MEASURE what the original does to its data: run a SQL Server trace and a DB before/after diff, and record both as OBS. This is the raw material from which behavior rules (T-006) are later derived — black-box, never by reading the original's code. Observation-room task (`data-layer-behavior-trace` kind): faces the original via `app_driver` / `sql_trace` / `sql_query`; reads and writes only `observed/`.

## Branching Note

Branch one subagent per action or per screen via `hw branch T-003 action-NNN`. Subagents need `file_write`, `sql_trace`, `sql_query`.

## Step-by-Step Instructions

1. Recite OR-001 and the assigned screen/action OBS. SCAN (not a build-room task).
2. Snapshot the relevant tables (DB diff baseline) via `sql_query`.
3. Start a `sql_trace`. Perform the user action on the original (drive via `app_driver`).
4. Stop the trace. Capture the statements issued.
5. Re-snapshot the tables; compute the row-level before/after diff.
6. Write OBS: `observation_type: sql-trace` (the statements) and/or `db-diff` (the delta), `capture_method` matching, `source_ref` = action name. Store raw trace/diff under `observed/traces/` and reference in `artifact_path`.
7. `hw add observation < draft-obs-NNN.md`. Confirm `source: original`, `zone: observed`, `consumable_by_build: false`.
8. Repeat with varied inputs where the action's data effect is input-dependent (this seeds the worked_examples / oracle_cases for T-006).

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [OBS-NNN#…]
- **SCAN markers answered:** <count>
- **Zones read / written:** read: observed / written: observed
- **Outputs produced:** trace/diff OBS [OBS-… through OBS-…]; raw captures under observed/traces/
- **Input-dependent actions noted:** <list — these become behavior-rule worked_examples in T-006>
- **Ambiguous/hidden-state actions flagged:** <list for re-measurement>
- **Recommended follow-up:** "Spec room: behavior-rules (T-006) and data-dictionary (T-005) consume these OBS."
