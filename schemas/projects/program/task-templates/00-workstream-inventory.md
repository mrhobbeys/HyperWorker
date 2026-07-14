---
id: T-000
kind: task
schema: program
phase: A
phase_step: 1
risk_level: standard
required_tools: [file_read, file_write, hash_compute]
delivery_mode: constrained
depends_on: []
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "Every 'existing' entry in OR-001.initial_workstream_inventory was probed (bootstrap-probe.md sibling-instance-directory-sweep) and either confirmed or flagged declared-but-missing."
  - "Every confirmed existing instance is registered as a workstream artifact with origin: existing-registered, status populated from that instance's own active_project.md / most recent archived project."
  - "No 'new' entry from OR-001.initial_workstream_inventory was registered here — those route through T-002."
  - "bootstrap.inventory_diff has been emitted with declared/found/missing fields populated, OR bootstrap.probe_skipped was emitted with reason (only valid if OR-001.initial_workstream_inventory declares zero existing instances)."
  - "Operator reconciliation captured; bootstrap.scope_locked emitted with the locked per-item list."
  - "PROJECT.md §Scope is rewritten from bootstrap.scope_locked payload."
---

# Task T-000: Workstream Inventory

## Objective

Establish ground truth for every workstream this program starts with. Register each
confirmed existing sibling instance as a `workstream` artifact (`origin:
existing-registered`). Leave every declared "new" workstream unregistered — those go
through the T-002 spawn-and-pause protocol the first time the operator initiates
them, so the same operator-approval gate applies whether the program starts mid-flight
(the field's common case — see `reference/field-reports/2026-07-machine1-gather.md`
§A, "~14 concurrent instances") or from zero.

## Step-by-Step Instructions

1. Read OR-001. Note `program_goal`, `initial_workstream_inventory`,
   `rollup_cadence`, `lifecycle`.
2. **Read `schemas/projects/program/bootstrap-probe.md`.** Execute the
   sibling-instance-directory-sweep probe.
3. For each candidate directory the probe finds with a `.hyperworker/events.jsonl`,
   read `projects/active_project.md` (or the most recent archived/parked project)
   to determine `child_project_id`, `bootstrapped_from_schema`, `lifecycle`, and
   current status.
4. Cross-check against the "existing" entries in
   `OR-001.initial_workstream_inventory`. Anything declared but not found on disk
   is `declared-but-missing`; anything found but not declared is
   `missing_from_declared`.
5. Emit `bootstrap.inventory_diff` with the declared/found/missing lists populated
   (or `bootstrap.probe_skipped` if `initial_workstream_inventory` has zero
   existing entries).
6. **Reconcile with operator.** Surface the diff: per instance, operator confirms /
   excludes / corrects the path. Capture per-item dispositions.
7. **Emit `bootstrap.scope_locked`** with the reconciled per-item list.
8. For each confirmed instance, run `hw add workstream < draft-ws-NNN.md` with
   `origin: existing-registered`, `spawn_decision: null`, `premise: null`,
   `last_rollup_citation: null` (the first roll-up will populate it).
9. Update PROJECT.md §Scope from the locked list.
10. Answer @@SCAN markers from `00-REFERENCE-rules.md`.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…]
- **SCAN markers answered:** <count>
- **Outputs produced:** WS-001 through WS-NNN; bootstrap.inventory_diff EV-NNNN;
  bootstrap.scope_locked EV-NNNN (or bootstrap.probe_skipped)
- **Declared-but-missing instances:** <list with resolution — path corrected, or
  reclassified to "new" for T-002>
- **Instances excluded:** <list with reason>
- **Discoveries:** <e.g., "3 declared instances resolved cleanly; 1 path was stale (operator moved the workspace) and was corrected before registration">
- **Recommended follow-up:** "Run T-001 to stand up the registry projection."
