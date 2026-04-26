---
id: T-007
kind: task
schema: report-synthesis
phase: D
risk_level: elevated
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-006]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-NNN#hash] with synthesis_role: output-structure"
  - "ALL live [CLM-NNN#hash], [DEC-NNN#hash], [F-NNN#hash], [AP-NNN#hash] mapped to sections in the structure"
acceptance_criteria:
  - "Every section declared in the structure Decision is filled."
  - "Every claim or assertion in the draft cites at least one source artifact by hash ([SRC-…], [CLM-…], [DEC-…], [F-…])."
  - "Anti-patterns are referenced where the synthesis takes a contradicting direction; not silently dropped."
  - "Deferred contradictions appear in the open-questions section with their CTR-IDs."
  - "Draft is written to deliverable_path's draft location (e.g., `<deliverable_path>.draft.md`)."
---

# Task T-007: Synthesis Draft

## Objective

Fill the structure with cited content. This is where claims, decisions, findings, and anti-pattern references become a connected document. Layer 1 verification (citation completeness) and Layer 2 (synthesis_internal_consistency) check this draft.

## Step-by-Step Instructions

1. Read OR-001 and the structure Decision.
2. Read all consumed artifacts (claims, decisions, findings, anti-patterns mapped to sections per structure).
3. Recite the structure in your own words to `consumed-inputs.md` per the consumption protocol. Recite OR-001 fields. The recitation overlap check (default 0.7) enforces this.
4. Section by section, write the draft:
   - Open the section with its declared role.
   - For each claim or assertion, cite the source artifact by hash.
   - Where the section's content contradicts an anti-pattern (i.e., the AP captured a wrong direction), cite the AP and briefly state how the synthesis differs.
   - Where two related claims combine, cite both.
   - Use OR-001's voice anchor and Tier 4 STYLE rules.
5. The draft is saved to `{{ deliverable_path }}.draft.md` — never directly to the final deliverable_path. The final write happens only after T-008 audit and T-009 operator approval.
6. Answer @@SCAN markers, especially:
   - SCAN_1_1: Does every claim cite at least one source?
   - SCAN_3_2: Are there contradictions between sections?
7. Failure scenarios for elevated risk: document 2 — one for "what if the structure was wrong (e.g., reader cannot find a key answer)" and one for "what if a primary source was misinterpreted."

## Specific guidance

**Citation density matters.** Synthesis output that cites only at section boundaries fails Layer 1. Citations should appear at the claim level — every meaningful assertion has a hash reference. This produces dense citation-marked output. That's the point.

**Voice consistency.** If OR-001 declares a brand voice, apply it. Tier 4 STYLE rules apply but are overridden by Tier 1 source-fidelity if they ever conflict (they shouldn't — voice does not require unsupported claims).

**Internal consistency.** Two sections of the synthesis cannot make conflicting claims without an internal note. The Layer 2 `synthesis_internal_consistency` check scans for this.

**Anti-patterns visible.** Where the synthesis takes a different direction than an earlier-round AP, cite the AP and briefly note the supersession. This is the round-aware discipline making itself visible.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** <count of [SRC-…], [CLM-…], [DEC-…], [F-…], [AP-…] cited in the draft>
- **Sections filled:** <count from structure>
- **Anti-patterns referenced:** <list>
- **Draft path:** {{ deliverable_path }}.draft.md
- **Failure scenarios documented:** 2
- **SCAN markers answered:** <count>
- **Discoveries:** <e.g., "Two consumed claims contradicted each other and weren't caught in T-004; flagged for review">
