---
id: T-006
kind: task
schema: brand-ecosystem-audit
phase: D
risk_level: critical
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-005]
consumes: ["[OR-001#<short-hash>]", "[MAN-NNN#<short-hash>]"]
acceptance_criteria:
  - "Reads the manifest FIRST; begins with an Evidence Inventory (every file used) + an open-items table."
  - "Restates every property + the brand on ONE common scorecard scale."
  - "Emits >=3 `strategic-path` artifacts (pick/combine/sequence) with >=1 is_foundational; NOT one forced plan."
  - "Includes a decision-aid comparison table + recommended default + sequence (without forcing), foundational fixes regardless of path, unified funnel, consistency checklist, per-path metrics."
  - "Every claim grounded in a cited artifact; >=1 disconfirming finding addressed."
  - "Output written to OR.deliverable_path."
---

# Task T-006: Master Synthesis (the paths menu)

## Objective
Turn per-property ground truth into "where things should be": a menu the operator picks from.
Do NOT re-audit properties — synthesize.

## Steps
1. Read MAN-NNN first. Build the Evidence Inventory + open-items table.
2. Produce the report per the rules-template synthesis template: bottom line -> evidence
   inventory -> scorecard -> cross-board synthesis -> visibility picture -> identity backbone ->
   STRATEGIC PATHS MENU (write each as a `strategic-path` artifact) -> decision aid -> foundational
   fixes -> funnel -> consistency checklist -> per-path metrics.
3. Tag provenance; relabel any ASSUMED-only recommendation as a hypothesis. Write to deliverable_path.
4. Answer @@SCAN markers.

## Completion Report
- Acceptance: <X/Y> · Output: <deliverable_path> · Paths: PATH-001…NNN (foundational: <which>)
- Disconfirming addressed: <which> · Open items carried forward: <list>
