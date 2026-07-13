---
id: T-009
kind: task
schema: cleanroom-rebuild
phase: C
risk_level: critical
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-005, T-006, T-007, T-008]
consumes:
  - "[OR-001#<short-hash>]"
  - "[BR-NNN#<short-hash>]"    # every behavior-rule's oracle_cases
  - "[SPEC-NNN#<short-hash>]"  # screen / data-dictionary / hardware specs to cover
acceptance_criteria:
  - "The test oracle aggregates every behavior-rule's oracle_cases into a single spec-derived oracle the build room is verified against (recorded input->expected output)."
  - "Every BR has at least one oracle case in the oracle, and every oracle case maps to a BR or SPEC (Layer 2 oracle_case_coverage: no orphan rules, no orphan cases)."
  - "The oracle lives entirely in spec/ (consumable_by_build=true) and references NO path under observed/ — it must be readable by the walled build room."
  - "The oracle is derived from MEASURED cases (worked_examples / oracle_cases), NOT from re-running the original at verify time."
  - "This task is the spec->build boundary: it asserts every captured screen has a screen-spec and every measured rule has an oracle case before the build room opens."
  - "Zero Tier 1 violations from 00-REFERENCE-rules."
---

# Task T-009: Test Oracle  *(critical — spec->build boundary)*

## Objective

Assemble the spec-derived ORACLE: the single source of truth the walled build room is verified against. It aggregates every behavior-rule's `oracle_cases` and screen/hardware acceptance cases into `spec/oracle/`. This is the **spec->build boundary** — the moment the wall is crossed for real. The full council (including the `cleanroom-integrity-auditor` and `oracle-reality-calibrator`) fires on this critical task and at `phase.complete` for Phase C. Spec-room task (`spec-author` kind): reads `observed/` + `spec/`, writes only `spec/`.

## Step-by-Step Instructions

1. Recite OR-001 and every BR/SPEC. SCAN: confirm @@SCAN_3_1 (every screen/rule has a spec + oracle case) before assembling. Not a build-room task.
2. Aggregate every `oracle_case` from every BR into `spec/oracle/cases.md` (or per-domain files), each as recorded input->expected output.
3. Add screen-acceptance cases (from screen-specs) and hardware-output cases (from hardware-specs) where mechanically checkable.
4. **Coverage assertion:** confirm every BR has ≥1 oracle case and every captured screen (OBS screen) has a screen-spec. List any gap; do not open the build room with gaps.
5. **Wall readiness:** confirm the entire oracle lives in `spec/` and cites NO `observed/` path — the walled build room (T-011) must be able to read it. The oracle must NOT require re-running the original.
6. `hw add spec < draft-spec-oracle.md` (spec_type: other / oracle). Confirm `source: cleanroom`, `zone: spec`, `consumable_by_build: true`.
7. The phase.complete council fires automatically. Wait for `council.converged` before Phase D begins. Operator review required.

## Failure Scenarios (critical — three required)

1. **Scenario:** A behavior-rule has no oracle case; the build room implements it untested.  
   **Outcome:** <fill in>  
   **Safe?** <yes/no>
2. **Scenario:** An oracle case secretly depends on re-running the original (e.g., "compare to live total").  
   **Outcome:** <fill in — this is a wall breach; the oracle must be self-contained>  
   **Safe?** <yes/no>
3. **Scenario:** A captured screen has an unobserved branch with no spec, so the oracle never exercises it.  
   **Outcome:** <fill in>  
   **Safe?** <yes/no>

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [BR-NNN#…], [SPEC-NNN#…]
- **SCAN markers answered:** <count>
- **Zones read / written:** read: observed, spec / written: spec
- **Outputs produced:** oracle SPEC under spec/oracle/
- **Coverage:** <N BR with oracle cases / M total; K screens specced / L captured — must be complete>
- **Wall-readiness confirmation:** "Oracle lives in spec/ only; references no observed/ path; does not require running the original."
- **Recommended follow-up:** "OPERATOR REVIEW REQUIRED at spec->build boundary before T-010 opens the build room."
