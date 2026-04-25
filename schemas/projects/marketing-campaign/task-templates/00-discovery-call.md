---
id: T-000
kind: task
schema: marketing-campaign
phase: 1
risk_level: standard
required_tools: [file_write]
delivery_mode: constrained
depends_on: []
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "Audience description (segment, role, pain) captured."
  - "Single-sentence offer statement captured."
  - "Tier 1 BRAND-ABSOLUTE rules drafted with operator (zero violations possible by definition)."
  - "Hard deadline and budget reflected from OR-001 verbatim."
---

# Task T-000: Discovery — Audience, Offer, Brand Rules

## Objective

Run a structured discovery against the operator's stated campaign. Output is two artifacts: a finding capturing audience definition, and a decision capturing the offer statement. Tier 1 brand-absolute rules are co-drafted and added to `00-REFERENCE-rules.md`.

## Step-by-Step Instructions

1. Read `OR-001`. Confirm the audience segment is consistent with team and authority fields.
2. Ask the operator three questions: who is the target reader (role + size + pain), what does the offer let them do that they cannot today, and what brand-absolute rules apply (legal claims, regulated language, voice constraints).
3. Draft `F-001` capturing audience description with `confidence: provisional`. Run `hw add finding < draft-f-001.md`.
4. Draft `DEC-001` stating the single offer in one sentence. Run `hw add decision < draft-dec-001.md`.
5. Draft Tier 1 BRAND-ABSOLUTE rules in `00-REFERENCE-rules.md`. The rules live in the file, not as artifacts; the operator confirms before exit.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…]
- **SCAN markers answered:** <count>
- **Outputs produced:** F-001, DEC-001, 00-REFERENCE-rules.md (Tier 1 populated)
- **Discoveries:** <items the executor surfaces; planner decides whether to write findings/anti-patterns>
- **Recommended follow-up artifacts:** "Promote F-001 to validated once a second source confirms the audience description" / "none"
