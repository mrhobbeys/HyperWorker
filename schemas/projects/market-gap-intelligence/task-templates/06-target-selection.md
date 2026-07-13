---
id: T-006
kind: task
schema: market-gap-intelligence
phase: C
risk_level: elevated
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-002, T-003]
consumes:
  - "[OR-001#<short-hash>]"
  - "[FP-NNN#<short-hash>]"
  - "[GAP-NNN#<short-hash>]"
acceptance_criteria:
  - "Each candidate cluster scored on Demand, Commercial, Winnability, Fit (1-5), every score citing a MEASURED/OBSERVED artifact by hash."
  - "Targets ranked by rank_score = product of the four axes."
  - "Top targets carry ESTIMATED funnel math with formula, MEASURED inputs, and a low/mid/high band."
  - "fit_score sourced from the client where possible; if still ASSUMED, the target is marked needs-client-confirmation and may not be the sole basis of an irreversible move."
  - "No target recommends out-content-ing a serp-trap (cross-check T-001 channel findings)."
---

# Task T-006: Target Selection (Q4 — what should we rank for?)

## Objective
Converge the discovery + gap evidence into a ranked, winnable, commercial,
on-brand target list with funnel math for the top picks. This is where projections
are ALLOWED — because they are arithmetic on MEASURED inputs with a visible band,
not vibes.

## Step-by-Step
1. Assemble candidate clusters from FP gaps + GAP money gaps + competitor moats
   worth contesting.
2. Score each 1–5, each axis citing evidence:
   - Demand [MEASURED volume/trend] · Commercial [MEASURED CPC/intent] ·
     Winnability [OBSERVED/ESTIMATED vs SERP owners + domain strength + effort] ·
     Fit [client-confirmed; ASSUMED until then].
3. rank_score = Demand × Commercial × Winnability × Fit. Sort.
4. For top targets, funnel math (keyword-scanner model): cost-per-job = CPC ÷
   LP-conversion ÷ close; monthly = jobs × cost-per-job; show low/mid/high. Label
   every input's provenance.
5. Cross-check T-001 channel findings: drop or reframe any target sitting on a
   trap-owned SERP. Write TGT artifacts with suggested_action.
6. Append to evidence log. Answer @@SCAN markers.

## Completion Report
- Acceptance criteria: <X/Y>
- Citations consumed: [OR-001#…], [FP/GAP-NNN#…]
- Outputs: TGT-001…NNN (ranked)
- Top 3 targets + funnel band: <…>
- Targets needing client fit-confirmation: <list>
