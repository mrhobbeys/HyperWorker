---
id: T-008
kind: task
schema: market-gap-intelligence
phase: D
risk_level: critical
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-004, T-005, T-006, T-007]
consumes:
  - "[OR-001#<short-hash>]"
  - "[TGT-NNN#<short-hash>]"
  - "[DEC-NNN#<short-hash>]"
  - "[AP-NNN#<short-hash>]"
acceptance_criteria:
  - "Every recommendation cites ≥1 MEASURED/OBSERVED artifact by hash, or an ESTIMATED value on measured inputs. No recommendation rests on ASSUMED-only inputs (those appear as labeled hypotheses-to-test)."
  - "The deliverable leads with the decision + evidence, addresses the strongest counter-evidence (≥1 disconfirming finding cited), and honors brand_constraints."
  - "Captured anti-patterns are referenced where the recommendation takes a different direction — not silently dropped."
  - "Where a tool was unavailable, the affected section is explicitly marked a hypothesis-to-verify."
  - "Output written to OR-001.deliverable_path; the anti-hallucination checklist (rules-template §Checklist) passes."
---

# Task T-008: Recommendation Synthesis

## Objective
Produce the cited decision report that answers OR-001.decision_statement. This is
the deliverable; T-009 audits it.

## Step-by-Step
1. Read OR-001, all TGT/DEC/AP artifacts, and findings.
2. Structure: (a) the decision in one paragraph, (b) what the evidence shows
   (competitors, footprints, gaps — cited), (c) the ranked targets + funnel math,
   (d) the channel calls, (e) the strongest counter-evidence and why the
   recommendation still holds, (f) what to verify next + the cheapest experiments.
3. Fill open anti-pattern superseding_direction citations now that decisions exist.
4. Tag every claim's provenance; relabel any ASSUMED-only recommendation as a
   hypothesis. Run the anti-hallucination checklist.
5. Write to deliverable_path. Answer @@SCAN markers.

## Completion Report
- Acceptance criteria: <X/Y>
- Citations consumed: <all consumed artifact IDs>
- Output: <deliverable_path>
- Disconfirming evidence addressed: <which>
- Hypotheses-to-verify (tool-gap or ASSUMED): <list>

## Synthesis output template (v1.1 — adopted from a prior pilot engagement's master-report shape)
Structure the deliverable as a **menu of paths**, never one forced plan:
1. **Bottom line in one sentence.**
2. **Evidence Inventory** — table of every source used (file → unit → type) PLUS an
   **"open items / not-yet-run"** table (what's missing + what it would have told us).
   Makes provenance auditable and surfaces tool-gaps as explicit hypotheses.
3. **Scorecard on ONE common scale** across all units.
4. **Cross-board synthesis** — recurring themes, each grounded in a specific quote/number.
5. **Consolidated visibility picture** — how it's seen/found now vs how it should be.
6. **Identity/positioning backbone** — the one standard everything else depends on.
7. **Strategic Paths — the menu (core deliverable):** 3-6 coherent paths the operator
   can pick / combine / sequence. Each: goal, core idea, levers/units used, effort,
   expected payoff, time-to-result, risks, top 3-5 moves. NEVER one fixed plan.
8. **Decision aid** — comparison table (effort × payoff × time × units touched) + a
   recommended *default* and *sequence* for "just tell me the obvious order," without forcing it.
9. **Foundational fixes to do regardless of path** — decouple quick wins from the strategy decision.
10. **Unified funnel + consistency checklist + per-path metrics.**
