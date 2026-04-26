---
id: T-006
kind: task
schema: report-synthesis
phase: D
risk_level: elevated
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-005]
consumes:
  - "[OR-001#<short-hash>]"
  - "ALL [DEC-NNN#hash] with synthesis_role: contradiction-resolution"
acceptance_criteria:
  - "A Decision artifact declares the synthesis output structure (sections, ordering, format) before drafting begins."
  - "Decision references OR-001.output_format and shows how the structure realizes that format."
  - "Decision lists which claims/decisions/findings each section will draw from (mapping)."
  - "If output_format declared a specific shape (e.g., 'decision matrix with N rows'), the structure conforms."
---

# Task T-006: Synthesis Structure Decision

## Objective

Decide the output structure before drafting. The structure is a Decision artifact (synthesis_role: output-structure) that downstream drafting consumes. Locking structure first prevents drift during drafting.

## Step-by-Step Instructions

1. Read OR-001. Note `synthesis_purpose`, `target_audience`, `output_format`.
2. Read all resolved Decisions from T-005. Read live claims and findings.
3. Sketch a structure that:
   - Realizes OR-001.output_format (e.g., decision-matrix → N rows; structured-doc → ordered sections; executive-brief → exec summary + key sections).
   - Serves OR-001.synthesis_purpose. The structure should make the purpose immediately legible to the audience.
   - Maps content to sections. For each section: which claims, which decisions, which findings, which anti-pattern references.
4. If multiple structures are plausible (e.g., "by topic" vs. "by source weight" vs. "by recommendation strength"), evaluate each briefly. Capture the alternatives in `alternatives_considered`.
5. Write Decision artifact. `synthesis_role: output-structure`. The body of the decision describes the structure as a hierarchical outline with section-to-content mapping.
6. Run `hw add decision < draft-dec-NNN.md`.
7. Council fires (Phase D entry). `operator-goal-aligner` reviews to confirm structure realizes OR-001.
8. Answer @@SCAN markers.

## Specific guidance

**Map claims to sections explicitly.** Don't write a structure with empty sections or sections whose content is "we'll figure it out during drafting." Every section must declare what it draws from. If a section can't be filled by registered content, either remove it or capture an open question.

**Anti-pattern integration.** Where the synthesis takes a direction that contradicts an anti-pattern (i.e., a wrong direction from an earlier round), the structure should reference the AP to make the supersession visible. This is part of the round-aware discipline.

**Deferred contradictions.** Open questions section. Deferred contradictions appear there with their `nature` and the operator-approved reason for deferral.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [DEC-…]
- **Structure decision:** [DEC-NNN#hash]
- **Sections declared:** <count>
- **Alternative structures considered:** <count>
- **Deferred contradictions placed in open-questions section:** <list>
- **SCAN markers answered:** <count>
