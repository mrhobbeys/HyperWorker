---
id: T-011
kind: task
schema: cleanroom-rebuild
phase: D
risk_level: critical
executor: local_model            # WALLED: runs on OR-001.build_executor, NOT the orchestrator
required_tools: [file_read, file_write, test_run]
forbidden_tools: [app_driver, gui_driver, sql_trace, browser, decompiler]
forbidden_reads: [observed]      # oracle cases live in spec/; MAY NOT read observed/ or run the original
no_smoke_run: true               # verification compares the new app to the spec-derived ORACLE, never to the original
no_peek: true
delivery_mode: prescribed
depends_on: [T-010]
consumes:
  - "[OR-001#<short-hash>]"
  - "[SPEC-NNN#<short-hash>]"  # the test oracle (T-009) lives in spec/
  - "[BR-NNN#<short-hash>]"    # behavior-rules whose oracle_cases are checked
acceptance_criteria:
  - "The built app is run against the spec-derived ORACLE (recorded input->expected output from T-009 / BR oracle_cases). PASS requires every oracle case to pass."
  - "PASS/FAIL is judged vs the ORACLE, NOT vs the original. The original is never run or compared against (no_smoke_run); @@SCAN_1_3 answers 'no'."
  - "This task ran on executor=local_model bound to OR-001.build_executor (Layer 1 build-executor-isolation)."
  - "No OBS and no path under observed/ is cited or read (Layer 1 build-no-observed-read); inputs are SPEC/BR + src/ only."
  - "Failing oracle cases are recorded; each is routed to a fix in T-010 or a DEC if the oracle case itself is wrong (deviates_from_spec)."
  - "Zero Tier 1 violations from 00-REFERENCE-rules."
---

# Task T-011: Verify Against Oracle  *(critical — WALLED, local executor)*

## Objective

Run the built app against the spec-derived ORACLE and record PASS/FAIL per case. **Correctness is judged against the oracle, never against the original.** This task runs `executor: local_model` on `OR-001.build_executor`. It reads `spec/` (where the oracle lives) and `src/`; it may NOT read `observed/`, run the original (no smoke run), or read its binaries/decompilation (no peek). The `oracle-reality-calibrator` and `cleanroom-integrity-auditor` council members fire on this critical task.

## Wall constraints (read before any state-changing action)

- **Verify against the oracle, not the original.** The oracle (T-009) is self-contained in `spec/`. If a case says "compare to the live original," that is a wall breach in the oracle — block and route back to T-009.
- **Inputs are SPEC/BR + src/ only.** No `observed/`. No running the original.
- **You are the local model.** If running on the orchestrator, STOP (Layer 1 build-executor-isolation).

## Step-by-Step Instructions

1. Recite OR-001, the oracle SPEC, and the BR being checked. SCAN: @@SCAN_1_1 (cites only SPEC/BR), @@SCAN_1_2 (executor=local_model), @@SCAN_1_3 (did not run/peek the original — answer 'no').
2. For each oracle case, run the built app with the recorded input via `test_run` and capture the actual output.
3. Compare actual vs `expected_output` from the oracle case. Record PASS/FAIL per case.
4. For each FAIL: determine whether the build is wrong (route a fix back to T-010) or the oracle case is wrong (write a `DEC-XXX`, `deviates_from_spec`, and re-derive the case from measured OBS in the spec room — never by re-checking the live original here).
5. Record the overall pass rate. PASS only when every oracle case passes.
6. Write the results to `src/` (test reports / verification log). Run `hw write --status complete` after the wall SCANs are answered.

## Failure Scenarios (critical — three required)

1. **Scenario:** An oracle case fails and you are tempted to run the original to "see what it should do."  
   **Outcome:** <fill in — the correct move is route to T-010 or re-derive in the spec room; never smoke-run the original>  
   **Safe?** <yes/no>
2. **Scenario:** The oracle is missing a case for a screen branch, so the built app passes despite a real defect.  
   **Outcome:** <fill in — gap routes back to T-009/T-006>  
   **Safe?** <yes/no>
3. **Scenario:** A subagent for parallel test execution is provisioned with sql_trace (could reach the original DB).  
   **Outcome:** <fill in — capability gates refuse; record the refusal>  
   **Safe?** <yes/no>

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [SPEC-NNN#…], [BR-NNN#…]  (NO OBS — by construction)
- **SCAN markers answered:** <count, including the three Tier 1 wall SCANs>
- **Executor:** local_model on <OR-001.build_executor id> (confirm NOT orchestrator)
- **Zones read / written:** read: spec, src / written: src
- **Judged against:** "spec-derived oracle (T-009) — NOT the original; no smoke run, no peek"
- **Oracle pass rate:** <N/M cases pass>
- **Failing cases:** <list with routing: fix in T-010 / oracle-DEC>
- **Recommended follow-up:** "If all oracle cases pass, route to project.archive (final cleanroom-integrity-auditor fire)."
