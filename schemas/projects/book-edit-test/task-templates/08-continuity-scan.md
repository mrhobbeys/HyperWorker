---
id: T-008
kind: task
schema: book-edit-test
phase: C
risk_level: elevated
required_tools: [file_read, file_write, docx_handling]
delivery_mode: constrained
depends_on: [T-007]
consumes:
  - "[OR-001#<short-hash>]"
  - "[VA-001#<short-hash>]"
  - "[AM-001#<short-hash>]"
  - "ALL post-edit [SRC-NNN#hash] with source_role: post-split-chapter (current hash, post-Phase-B)"
  - "ALL applied [EP-NNN#hash] (edit_proposals applied in Phase B)"
acceptance_criteria:
  - "Cross-chapter pairwise scan completed for: character-name consistency, term consistency, framework-name consistency, product-name consistency, internal-reference resolution (forward and backward), example consistency."
  - "Each inconsistency or contradiction is registered as a contradiction artifact (CTR-NNN) with claims (the conflicting locations cited by chapter and paragraph), nature (factual | recommendation-conflict | scope-conflict | terminology-drift | reference-broken), and status: open."
  - "Layer 2 internal_reference_resolution_check produces a structured report: every 'see Chapter N', 'as we'll see later', 'as discussed earlier' reference resolved or flagged."
  - "False-positive ruled-compatible cases are listed in completion report with reason."
---

# Task T-008: Continuity Scan

## Objective

Walk the post-edit chapter corpus pairwise (and against itself) and surface cross-chapter inconsistencies. Each contradiction becomes a typed artifact for T-009 to resolve. The scan is heuristic where ambiguity is unavoidable (e.g., when two chapters describe the same example with different emphasis); the agent's judgment plus operator confirmation handle the borderline cases.

## Step-by-Step Instructions

1. Read OR-001, VA-001, AM-001, all post-edit chapter source artifacts, and all applied edit_proposals.
2. **Build a cross-chapter index:**
   - Named entities (persons, companies, products, frameworks, tools): walk each chapter, extract proper-noun-pattern tokens; for each, record `{token, chapter_id, paragraph_index, surface_form}`.
   - Internal references: extract every "see Chapter N", "as we saw in Chapter N", "as we'll see in Chapter N", "earlier we discussed", "later we'll cover" pattern; record `{phrase, source_chapter, target_chapter_or_section, paragraph_index}`.
   - Examples and case studies: extract every "for example", "consider", named-example markers; record `{example_marker, chapter_id, paragraph_index, brief_excerpt}`.
3. **Pairwise consistency check:**
   - For each named entity that appears in 2+ chapters, confirm surface forms match (e.g., "Slack" vs "slack" vs "the Slack platform"). Drift flagged.
   - For each internal reference, resolve the target. Forward reference: does the target chapter exist and contain content the reference describes? Backward reference: does the prior chapter contain it? References that don't resolve flagged.
   - For each example used in multiple chapters, compare the wording. Material differences (changed numbers, changed sequences, changed protagonist names) flagged.
4. **Register contradictions** for each flagged inconsistency:
   - `nature`: factual (e.g., chapter 3 says X happened in 2018, chapter 7 says X happened in 2019), recommendation-conflict (chapter 4 advises A, chapter 9 advises not-A), scope-conflict, terminology-drift (named entity surface form drift), reference-broken (internal reference doesn't resolve).
   - `claims`: list the conflicting locations as citations.
   - `status: open`.
   - Run `hw add contradiction < draft.md`.
5. **False-positive triage.** Some flags will be voice-of-author choices (deliberately re-emphasizing a point in different words across chapters; using a casual surface form once and a formal one elsewhere where each fits its chapter's register). Note these in the completion report as ruled-compatible with reason; do NOT register a contradiction for them.
6. **Internal-reference resolution report.** Produce a structured table: every reference, its target, resolution status (resolved | unresolved-target-missing | unresolved-content-missing | ambiguous). Append to the completion report.
7. Answer @@SCAN markers.

## Specific guidance

**Topic clustering not required.** Inherited from report-synthesis T-004's pairwise approach, but the book-edit case is structurally smaller: 10-15 chapters, not 50-200 claims. Pairwise across chapter-bounded entity references is tractable without clustering.

**Voice-of-author flexibility.** The same author can use "Slack" in one chapter and "the messaging platform we use" in another. This is voice consistency, not terminology drift. Drift is a problem only when the same surface form drifts to a different one across chapters with no contextual reason. Use VA-001 to inform judgment.

**Reference-broken is a hard fail.** A "see Chapter 7" with no chapter-7 content matching the reference is broken at the reader level. Always register as a contradiction even if the agent thinks it might be a phrasing-not-reference.

**Examples consistency is a Tier 1 enforcement.** A real example used in two chapters with different particulars is a Tier 1 violation (examples are preserved verbatim). Flag every instance.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [VA-001#…], [AM-001#…], [SRC-…], [EP-…]
- **SCAN markers answered:** <count>
- **Chapters scanned:** <list>
- **Cross-chapter index:** <named-entity-tokens count, internal-reference count, example-marker count>
- **Contradictions registered:** CTR-NNN through CTR-MMM
- **By nature:** factual=<n>, recommendation-conflict=<n>, scope-conflict=<n>, terminology-drift=<n>, reference-broken=<n>
- **Ruled compatible (not registered):** <list with reason>
- **Internal-reference resolution table summary:** resolved=<n>, unresolved-target-missing=<n>, unresolved-content-missing=<n>, ambiguous=<n>
- **Failure scenarios documented (per elevated risk):** 2
- **Discoveries:** <e.g., "ch-04 and ch-09 give conflicting recommendations on the same scenario; will need T-009 resolution">
- **Recommended follow-up:** "T-009 continuity-resolution can run; if any reference-broken contradictions resolve to a chapter pass that needs revision, that chapter's T-007 branch may need to re-fire."
