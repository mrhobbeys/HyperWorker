---
id: T-010
kind: task
schema: cleanroom-rebuild
phase: D
risk_level: critical
executor: local_model            # WALLED: runs on OR-001.build_executor (LM Studio), NOT the orchestrator
required_tools: [file_read, file_write]
forbidden_tools: [app_driver, gui_driver, sql_trace, sql_query, screenshot, browser, web_fetch, vision_describe, decompiler]
forbidden_reads: [observed]      # hard wall: build context never contains original-derived imagery/code
no_smoke_run: true               # must not run the ORIGINAL to check behavior
no_peek: true                    # must not read original binaries / decompilation
delivery_mode: constrained
depends_on: [T-009]
consumes:
  - "[OR-001#<short-hash>]"
  - "[SPEC-NNN#<short-hash>]"  # screen / data-dictionary / hardware specs ONLY
  - "[BR-NNN#<short-hash>]"    # behavior-rules ONLY
acceptance_criteria:
  - "The target app is implemented in OR-001.deliverable_path from SPEC/BR ONLY. Every original-derived behavior in the code cites a SPEC or BR by hash; NO OBS and NO path under observed/ appears in any build event (Layer 1 build-no-observed-read)."
  - "This task ran on executor=local_model bound to OR-001.build_executor, not the orchestrator (Layer 1 build-executor-isolation)."
  - "The original was never run and its binaries/decompilation never read (no_smoke_run / no_peek); @@SCAN_1_3 answers 'no'."
  - "The build wrote only to src/ (Layer 1 zone-write-discipline); it did not write into observed/ or spec/."
  - "Any deviation from a SPEC/BR is recorded as a DEC-XXX with deviates_from_spec set — no undocumented edits."
  - "Zero Tier 1 violations from 00-REFERENCE-rules."
---

# Task T-010: Build From Spec  *(critical — WALLED, local executor)*

## Objective

Implement the target application in `OR-001.deliverable_path` from SPEC/BR ONLY, on the isolated local executor. **No path to the original exists in this context.** This task runs `executor: local_model` on `OR-001.build_executor` — an endpoint with no `app_driver` and no network-to-original capability. The build room cannot read `observed/`, cannot run the original (no smoke run), and cannot read its binaries or decompilation (no peek). Capability gates refuse delegation if a subagent's tools intersect `forbidden_tools` or its read-scope includes `observed`.

## Wall constraints (read before any state-changing action)

- **Inputs are SPEC/BR only.** You may read `spec/` and `src/`. You may NOT read `observed/`. If you find yourself wanting an OBS, the spec is incomplete — block with `reason: spec_gap` and route back to the spec room (T-005–T-008). Do NOT reach for the original.
- **No smoke run.** Do not run the ORIGINAL to check behavior. Correctness is judged in T-011 against the spec-derived oracle.
- **No peek.** Do not read the original's binaries, decompilation, or source.
- **You are the local model.** If this task is somehow running on the orchestrator (which can reach the original), STOP — that is a wall breach (Layer 1 build-executor-isolation).

## Step-by-Step Instructions

1. Recite OR-001 and the consumed SPEC/BR. SCAN: @@SCAN_1_1 (cites only SPEC/BR), @@SCAN_1_2 (executor=local_model on build_executor), @@SCAN_1_3 (did not run/peek the original — answer 'no').
2. Implement the data layer from the data-dictionary SPEC, honoring OR-001.data_strategy.
3. Implement screens from the screen-specs and navigation-spec.
4. Implement business logic from the behavior-rules' `rule_statement`; use their `worked_examples` as inline expectations.
5. Implement peripheral I/O from the hardware-specs (protocol literals per canonical facts).
6. Where a SPEC/BR is ambiguous or contradictory, write a `DEC-XXX` (`room: build`, `deviates_from_spec` if you deviate) — never invent behavior by guessing at the original.
7. Write only to `src/`. Run `hw write --status complete` only after the wall SCANs are answered.

## Failure Scenarios (critical — three required)

1. **Scenario:** A spec is silent on an edge case and you are tempted to "just check the original."  
   **Outcome:** <fill in — the correct move is block with spec_gap, not peek>  
   **Safe?** <yes/no>
2. **Scenario:** A subagent dispatched for a subtask is provisioned with sql_query (could reach the original DB).  
   **Outcome:** <fill in — capability gates refuse; record the refusal>  
   **Safe?** <yes/no>
3. **Scenario:** The build deviates from a BR because the BR seems wrong.  
   **Outcome:** <fill in — record a DEC with deviates_from_spec; do not silently "fix" toward a remembered original behavior>  
   **Safe?** <yes/no>

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [SPEC-NNN#…], [BR-NNN#…]  (NO OBS — by construction)
- **SCAN markers answered:** <count, including the three Tier 1 wall SCANs>
- **Executor:** local_model on <OR-001.build_executor id> (confirm NOT orchestrator)
- **Zones read / written:** read: spec, src / written: src
- **Original run or read?** "no — no smoke run, no peek"
- **Outputs produced:** <paths under deliverable_path>
- **Deviations recorded:** <DEC-XXX list with deviates_from_spec, or 'none'>
- **Spec gaps blocking build:** <list routed back to spec room, or 'none'>
- **Recommended follow-up:** "Verify-against-oracle (T-011)."
