---
id: T-006
kind: task
schema: cleanroom-rebuild
phase: C
risk_level: elevated
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-003, T-005]
consumes:
  - "[OR-001#<short-hash>]"
  - "[OBS-NNN#<short-hash>]"  # the sql-trace / db-diff OBS the rule is measured from
  - "[SPEC-NNN#<short-hash>]"  # data-dictionary SPEC for field semantics
acceptance_criteria:
  - "Each measured business rule (pricing, tax, discount, mix-match, rounding, validation) is captured as a behavior-rule (BR) with a rule_statement (algorithm, our own words), worked_examples (input->output, measured), and oracle_cases (input->expected output)."
  - "Each BR cites the OBS it was measured from in derived_from (at least one); rules are derived from black-box experiments, NOT from reading code."
  - "Every BR has at least one worked_example and at least one oracle_case (Layer 1 oracle-case-present)."
  - "Money-touching rules (pricing/tax/discount/rounding) include boundary worked_examples (zero, max, rounding edges, negative/refund)."
  - "All BR carry source=cleanroom, zone=spec, consumable_by_build=true; this task reads observed+spec and writes only spec/."
  - "Zero Tier 1 violations from 00-REFERENCE-rules."
---

# Task T-006: Behavior Rules  *(elevated)*

## Objective

Re-express the original's MEASURED business logic as `behavior-rule` (BR) artifacts: algorithm + worked input->output examples + oracle cases, all derived from the black-box experiments captured in T-003. Spec-room task (`spec-author` kind): reads `observed/` + `spec/`, writes only `spec/`. Reading the original's code or decompilation to author a rule is a wall breach in `pure-black-box` strictness.

## Step-by-Step Instructions

1. Recite OR-001, the relevant trace/diff OBS, and the data-dictionary SPEC. SCAN: confirm @@SCAN_2_1 / @@SCAN_2_2. Not a build-room task.
2. For each measured rule, state the algorithm in `rule_statement` — precise enough to implement without seeing the original.
3. Populate `worked_examples` from the measured input->output pairs in the trace/diff OBS. Cite the originating OBS in each example's `measured_via` where individually traceable.
4. If the measurements do not yet cover the rule's boundaries, request additional black-box experiments (re-run T-003 with boundary inputs) rather than inferring from code.
5. Populate `oracle_cases` with the recorded input->expected-output cases the built app will be verified against (these flow into the T-009 oracle).
6. Cite all source OBS in `derived_from`.
7. `hw add behavior-rule < draft-br-NNN.md`. Confirm `source: cleanroom`, `zone: spec`, `consumable_by_build: true`.

## Failure Scenarios (elevated — two required)

1. **Scenario:** A rule was measured from too few inputs and the algorithm is overfit to the examples.  
   **Outcome:** <fill in — how would the oracle catch it?>  
   **Safe?** <yes/no>
2. **Scenario:** A money rule's rounding behavior at a boundary (e.g., half-cent) was not measured.  
   **Outcome:** <fill in>  
   **Safe?** <yes/no>

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [OBS-NNN#…], [SPEC-NNN#…]
- **SCAN markers answered:** <count>
- **Zones read / written:** read: observed, spec / written: spec
- **Outputs produced:** behavior-rule [BR-… through BR-…]
- **Rules needing more measurement:** <list — re-run T-003 with boundary inputs>
- **Recommended follow-up:** "Test-oracle (T-009) aggregates these oracle_cases."
