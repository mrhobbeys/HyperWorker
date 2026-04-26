---
id: T-001
kind: task
schema: report-synthesis
phase: A
risk_level: standard
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-000]
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "OR-001 completed with synthesis_purpose, target_audience, output_format, weighting_rule, excluded_topics, deliverable_path."
  - "Operator confirms OR-001 fields verbally or via Verification Checkpoint."
  - "00-REFERENCE-rules.md Tier 4 STYLE populated (citation format, voice anchor if applicable)."
  - "If operator has banned tokens or canonical facts for the deliverable audience, those tables in 00-REFERENCE-rules.md are populated."
---

# Task T-001: Synthesis Charter

## Objective

Lock the synthesis purpose, audience, output format, weighting rule, scope, and deliverable path. This is the operator's commitment to what the synthesis is FOR. Everything downstream consumes OR-001.

## Step-by-Step Instructions

1. Read existing OR-001 (created at bootstrap). Confirm all fields are populated.
2. If any field is null or vague, ask the operator. Specifically:
   - **synthesis_purpose:** must be a single concrete sentence. "Inform Q3 brand pivot decisions" is good; "Make sense of the reports" is too vague.
   - **target_audience:** specific role + decision-context. "Operator only, for personal strategic alignment" or "Marketing team + CEO, for funding-round narrative." Not "internal stakeholders."
   - **output_format:** declares structure. "Decision matrix with N rows, one per pivot question" or "Structured doc with sections: position, voice, segmentation, funnel architecture."
   - **weighting_rule:** how to handle multi-round sources.
   - **excluded_topics:** list, may be null.
3. If operator wants the synthesis to follow a specific voice or formatting, populate Tier 4 STYLE in `00-REFERENCE-rules.md`.
4. If the deliverable audience has banned tokens or canonical facts (e.g., regulated industry language, brand voice anchors), populate those tables.
5. Verification Checkpoint fires here. Council role `operator-goal-aligner` reviews OR-001 for sufficiency before extraction begins.
6. Answer @@SCAN markers.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…]
- **Operator confirmations:** <list of fields the operator explicitly approved>
- **SCAN markers answered:** <count>
- **Outputs produced:** OR-001 (updated), 00-REFERENCE-rules.md (Tier 4 + optional tables populated)
- **Discoveries:** <e.g., "Operator clarified that 'final-corrected' rounds are primary; initial rounds are contextual">
