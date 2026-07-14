---
id: T-004
kind: task
schema: market-gap-intelligence
phase: C
risk_level: elevated
required_tools: [file_read, file_write, browser]
delivery_mode: constrained
depends_on: [T-001, T-003]
condition: "OR-001.scope_mode == 'vertical-choice'"
consumes:
  - "[OR-001#<short-hash>]"
  - "[CMP-NNN#<short-hash>]"
  - "[GAP-NNN#<short-hash>]"
acceptance_criteria:
  - "Each candidate vertical scored 1-5 on all six dimensions, every score provenance-tagged and citing evidence."
  - "Competitor TYPE per vertical is explicit (beatable businesses vs unbeatable software/aggregators)."
  - "At least one disqualifier check run per vertical (intent mismatch / no specialization premium / wrong channel / capability gap)."
  - "A vertical-posture Decision (DEC, intel_role: vertical-posture) is written with alternatives_considered and a CHEAP confirming experiment named."
---

# Task T-004: Vertical Evaluation (niche vs generalist / which market)

## Objective
Decide whether a market is worth entering or leading with — empirically, not as a
branding preference. A niche beats generalist only when specialization MEASURABLY
raises trust/close-rate or lowers acquisition cost enough to offset the smaller
pool. Runs only when scope_mode == vertical-choice.

## Step-by-Step
1. List candidate verticals (include "generalist/broad" as a column if live).
2. Score each 1–5, tagging provenance and citing evidence:
   - Demand depth (volume + buyer population) [MEASURED]
   - Competitive density & TYPE (run/read T-001; beatable vs trap) [OBSERVED]
   - Commercial intensity (CPC, deal size, LTV) [MEASURED/ESTIMATED]
   - Defensibility / specialization premium (do buyers search for a specialist? do
     specialists charge more? is there a compliance/language barrier generalists
     fail?) [OBSERVED]
   - Channel reality (where buyers decide; local-ads-program eligibility e.g. LSA, if applicable) [OBSERVED]
   - Switching cost & sales cycle [OBSERVED/ASSUMED]
3. Run disqualifier checks: intent mismatch (money terms owned by software/
   product → buyer wants a tool, fatal for content entry), no specialization
   premium, wrong channel, capability gap.
4. Write the comparison and a vertical-posture Decision: posture (lead with X /
   stay generalist / add X as secondary / avoid), the evidence, and the cheapest
   reversible experiment to confirm before committing (e.g., one landing page +
   small ad test on the money term, measured for conversion before rebranding).
5. Append to evidence log. Answer @@SCAN markers.

## Completion Report
- Acceptance criteria: <X/Y>
- Outputs: F-NNN (six-dimension scores), DEC-NNN (vertical-posture)
- Recommended posture: <…>
- Disqualifiers found: <per vertical>
- Cheapest confirming experiment: <…>
