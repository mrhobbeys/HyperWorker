---
id: T-009
kind: task
schema: book-edit-test
phase: C
risk_level: elevated
required_tools: [file_read, file_write, docx_handling]
delivery_mode: constrained
depends_on: [T-008]
consumes:
  - "[OR-001#<short-hash>]"
  - "[VA-001#<short-hash>]"
  - "ALL [CTR-NNN#hash] with status: open"
  - "ALL post-edit [SRC-NNN#hash] for chapters referenced in any open contradiction"
acceptance_criteria:
  - "Every open contradiction has terminal status: resolved (with a Decision) OR deferred (with operator-approved reason)."
  - "Each resolution Decision (synthesis_role: continuity-resolution) cites the contradiction's CTR-NNN and the chapter sources involved, and articulates the chosen direction with rationale."
  - "If a resolution requires a chapter to be re-edited, a re-pass directive is captured: the chapter's T-007 branch re-fires with the resolution Decision in consumes:. The re-pass is bounded by the same bounded-iteration max_passes (3); if the chapter is already at 3 prior passes, the operator decides explicitly to re-pass (counter resets) or to defer."
  - "Re-passes that actuate produce paired external_state.read_back events per the live-edit primitive."
---

# Task T-009: Continuity Resolution

## Objective

For each open contradiction from T-008, write a Decision resolving it. If the resolution requires changes in a specific chapter, trigger that chapter's T-007 branch to re-fire with the resolution Decision as input. The polished manuscript at Phase D consumes only resolved or deferred-with-reason contradictions.

## Step-by-Step Instructions

1. Read OR-001, VA-001, all open contradictions, and the chapter sources involved in each contradiction.
2. **For each contradiction, decide a resolution path:**
   - **Direct resolution:** one location is correct, the other is not. Decision states which and why; the incorrect location's chapter re-passes to align.
   - **Synthesis:** both locations are partially correct; resolution articulates the unified statement; chapters re-pass to harmonize.
   - **Context-dependent:** both locations are correct in their respective contexts; resolution adds an internal note in one or both chapters acknowledging the difference; targeted re-passes apply the note.
   - **Deferral:** insufficient information to resolve; operator approves deferral; the contradiction is noted in the polished manuscript's open-questions section (if any) or in a Phase D follow-up backlog item.
3. **For each resolution:**
   - Write a Decision artifact. `synthesis_role: continuity-resolution`. `resolves_contradiction: [CTR-NNN#hash]`. `chapter_scope`: the chapter the resolution edits (or a list if multiple). Body: chosen direction, rationale, any specific text changes the resolution requires.
   - Run `hw add decision < draft.md`.
   - Update the contradiction artifact's status to `resolved` (via supersede event with `resolved_by: [DEC-NNN#hash]` populated).
4. **For deferrals:**
   - Confirm deferral reason with operator.
   - Update contradiction status to `deferred` with the operator-approved note.
5. **Schedule re-passes.** For each contradiction whose resolution requires chapter changes:
   - Identify the affected chapter(s).
   - Re-fire the chapter's T-007 branch with the resolution Decision added to its `consumes:`. The branch's pass counter increments (or resets if the operator authorized a fresh start).
   - The re-pass actuates per Phase B mechanics: edit_proposal → council → operator promote → live-edit → external_state.read_back.
   - If a chapter is at max_passes (3) already, the operator decides explicitly: authorize a counter reset (restart the bounded-iteration), defer the contradiction (no re-pass), or take over manually.
6. **After all re-passes complete and resolve their contradictions, update the contradictions' resolutions** with applied: true status references.
7. **Council fires** at Phase C end (continuity-watcher member) per council.yaml.
8. Answer @@SCAN markers.

## Specific guidance

**Use VA-001 to inform synthesis resolutions.** When two locations both have voice-fingerprint signal and the resolution articulates a unified statement, the unified statement should also match VA-001. A resolution that drifts the voice fails Tier 1.

**Document the loss.** Even when one location wins clearly, the Decision body captures what the other location said and why it was set aside. This preserves the lost-decision signal and helps Phase D's voice-guidelines doc capture the kinds of continuity drift the run encountered.

**Re-pass scope:** the re-pass works on the contradiction's region only, not the whole chapter. The edit_proposal for a re-pass should have a small edit_candidates count focused on the resolution's specific changes, not a fresh pass over the chapter. Layer 2 line_delta_pct should be small for re-passes; if it's not, surface as a flag (the re-pass scope is creeping).

**Deferred contradictions:** rare but acceptable. If deferred, the polished manuscript may include an internal note ("the question of X is beyond this book's scope") or simply leave the contradiction unaddressed if it doesn't bite the reader. Operator decides; this is captured in the deferral note.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [VA-001#…], [CTR-…], [SRC-…]
- **SCAN markers answered:** <count>
- **Contradictions resolved:** <count>
- **Contradictions deferred:** <count, with operator approval status>
- **Resolution Decisions:** DEC-NNN through DEC-MMM
- **Chapters re-passed:** <list with chapter_id → final EP-NNN>
- **Re-passes that hit max_passes (3):** <list, with operator's per-chapter resolution>
- **Failure scenarios documented (per elevated risk):** 2
- **Discoveries:** <e.g., "Reference-broken contradictions all resolved by adding small forward-pointer text in chapter 4; no re-passes hit max_passes">
- **Recommended follow-up:** "T-010 assembly can run; the polished manuscript reflects the resolved contradictions."
