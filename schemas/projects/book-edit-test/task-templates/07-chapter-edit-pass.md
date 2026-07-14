---
id: T-007
kind: task
schema: book-edit-test
phase: B
risk_level: elevated
required_tools: [file_read, file_write, docx_handling]
delivery_mode: live-edit
delivery_mode_fields:
  enumeration_required: true               # edit_candidates / create_candidates / delete_candidates per marketing-campaign live-edit shape
  preview_surface: "schemas/projects/book-edit-test/working/chapter-passes/ch-NN/"
  version_naming: "edit-proposal-ch-NN-pass-{pass}.md"
  convergence_criterion: "operator promotes edit_proposal OR three passes elapsed"
  max_passes: 3
requires_handoff_acknowledge: true
depends_on: [T-006]
branched_per: chapter
consumes:
  - "[OR-001#<short-hash>]"
  - "[VA-001#<short-hash>] (voice anchor)"
  - "[AM-001#<short-hash>] (assembly map — for chapter ID and original heading reference)"
  - "[SRC-NNN#<short-hash>] (the chapter's post-split source-of-truth file, current state)"
  - "ALL active [BP-NNN#hash] (banned-pattern artifacts: bootstrap seed + AI-indicator-research approvals)"
  - "ALL active [DEC-NNN#hash] with synthesis_role: preservation-rule"
  - "[DEC-NNN#hash] with synthesis_role: chapter-edit-philosophy and chapter_scope == this chapter (or project default if no override)"
  - "ALL [F-NNN#hash] with finding_kind in {unfinished-bit, placeholder-marker, incomplete-sentence, broken-internal-reference, ai-indicator-candidate} for this chapter"
  - "ALL [DEC-NNN#hash] with synthesis_role: unfinished-bit-disposition for this chapter"
  - "[DEC-NNN#hash] with synthesis_role: candidate-disposition (only fold-ins targeting this chapter)"
  - "Summaries-only of edit_proposals from previously-completed chapter passes (NOT full prior-chapter prose)"
acceptance_criteria:
  - "An edit_proposal artifact is produced enumerating edit_candidates, create_candidates, and delete_candidates per the live-edit primitive."
  - "Every edit_candidate has location, original_text, proposed_text, rationale (1 sentence), and tier_invoked (which precedence tier the change addresses)."
  - "Every create_candidate is authorized by an unfinished-bit-disposition Decision (expand) or candidate-disposition Decision (fold-in). Unauthorized create_candidates fail."
  - "Every delete_candidate is authorized by an unfinished-bit-disposition Decision (cut). Unauthorized delete_candidates fail."
  - "voice_drift_score (subagent self-assessment) is populated 0-1; line_delta_pct is computed against pre-pass line count."
  - "consumed_preservation_rules and consumed_banned_patterns enumerate the FULL active list of each, by hash. Missing any active rule or pattern fails Layer 1."
  - "Council members (voice-preservation-watcher, preservation-rule-watcher, edit-philosophy-aligner, banned-pattern-enforcer) all PASS. scope-shrink-watcher PASSes (every enumerated candidate has a disposition)."
  - "Layer 2 checks pass: voice_drift_score within philosophy cap; line_delta_pct ≤ max_line_delta_pct (project default or chapter override); banned_pattern_enforcement (substrate scan for banned-pattern instances in proposed_text); spelling_correction_floor; examples_preservation_check."
  - "After operator promotion (hw promote EP-NNN), the live-edit actuates: the chapter's post-split file is updated. external_state.read_back captures pre-pass and post-pass file hashes."
  - "post-pass file hash != pre-pass file hash (i.e., the live-edit actually changed the file). divergence_detected is false (pre and post differ as expected); divergence_detected is true if pre and post are identical (failure: edit didn't apply)."
---

# Task T-007: Chapter Edit Pass (branched per chapter)

## Objective

Produce a per-chapter edit proposal, get council convergence on it, surface to operator for promotion, and (after promotion) actuate the live edit against the chapter's post-split file. Repeat up to 3 passes if the proposal doesn't converge or operator returns for revisions.

This task is the heart of Phase B and is branched once per chapter at Phase B kickoff. Each branch (T-007.ch-01, T-007.ch-02, ...) is its own atomic unit, dispatched to a hermetic subagent.

## Branching Note

The parent T-007 is a rollup; the actual work happens in branches. At Phase B kickoff, the planner spawns one branch per chapter via `hw branch T-007 ch-NN` for every chapter in the assembly-map. Each branch is hermetic: the subagent sees only the consumed inputs above, NOT the operator dialog, NOT other chapters' prose (only summaries of prior chapters' edit_proposals).

The parent task folds back when all branches complete. The fold result is a 1-3 sentence summary per chapter (e.g., "ch-01: 2 passes; final EP-014 promoted; voice_drift 0.18; line_delta 22%").

## Step-by-Step Instructions (per branch)

1. **Recite** every consumed artifact to `consumed-inputs.md`. Recitation overlap threshold per the project's model profile (claude-opus-4-7: 0.65). Rewrite paraphrases that fall below threshold until accepted.
2. **Open the chapter's post-split file.** Note pre-pass: paragraph count, line count, file hash (sha256 of bytes).
3. **Read the chapter content.** Apply the philosophy declared in the chapter's chapter-edit-philosophy DEC (or project default).
4. **Enumerate edit_candidates.** Walk the chapter; for each correction, change, or improvement candidate:
   - Identify location (paragraph index + character range, or paragraph index alone if the change is paragraph-scope).
   - Capture original_text verbatim.
   - Compose proposed_text.
   - Write a 1-sentence rationale.
   - Note the tier_invoked: Tier 1 (banned pattern, examples preservation, voice preservation), Tier 2 (philosophy alignment), Tier 3 (spelling, grammar, internal-reference fix), or Tier 4 (style consistency).
5. **Enumerate create_candidates.** For every unfinished-bit finding for this chapter with disposition `expand`, propose new content. Each create_candidate:
   - Cites the finding's F-NNN.
   - Identifies the location (paragraph index where the new content goes — typically the paragraph the finding flagged).
   - Provides proposed_text.
   - Rationale: brief.
   For every candidate-disposition fold-in targeting this chapter, propose the fold-in as a create_candidate citing the finding and the candidate-disposition DEC.
6. **Enumerate delete_candidates.** For every unfinished-bit finding for this chapter with disposition `cut`, propose the deletion. Each delete_candidate cites the finding and disposition Decision and identifies the location and original_text being deleted.
7. **Compute voice_drift_score** (self-assessment 0-1). Compare proposed prose against VA-001 sample_excerpts in the same chapter; how much does the proposal preserve voice signature? 0 = no drift; 1 = wholesale rewrite. Honesty matters here; understating drift to pass council is a Tier 1 violation.
8. **Compute line_delta_pct.** (lines_added + lines_deleted + lines_modified) / lines_pre_pass × 100.
9. **Populate consumed_preservation_rules and consumed_banned_patterns** with the FULL active list by hash. Missing any active rule or pattern at this step fails Layer 1.
10. **Write the edit_proposal artifact.** Run `hw add edit_proposal < draft.md`. The artifact's `applied: false` (will be set true after promotion + actuation).
11. **Council fires automatically** on the edit_proposal task completion event (per council.yaml triggers). Members: voice-preservation-watcher, preservation-rule-watcher, edit-philosophy-aligner, banned-pattern-enforcer, scope-shrink-watcher (the last fires because delivery_mode: live-edit). Each emits a `council.report`. Convergence rule: all-agree-or-escalate.
12. **Surface to operator.** Brief: chapter ID, pass number, line_delta_pct, voice_drift_score, council verdicts (one line each), pointer to the working edit-proposal-ch-NN-pass-{pass}.md file for full details. Note any deferred or escalated council outcomes.
13. **Operator decision:**
    - **Promote** (`hw promote EP-NNN`): proceed to step 14.
    - **Revise** (operator gives directives): the directive is captured as a Decision (`synthesis_role: scope-decision` or `chapter-edit-philosophy` as appropriate); the branch re-fires from step 4 with the updated consumes; pass counter increments.
    - **Reject and defer**: the chapter's edit_proposal terminates with `applied: false`; the chapter is marked `deferred` in scope.complete; T-007 branch concludes without actuation. Operator notes the defer reason.
14. **Actuate the live edit.** With operator promotion, apply the proposal:
    - Open the chapter's post-split file.
    - Apply each edit_candidate, create_candidate, delete_candidate in declared order.
    - Save the file.
    - Compute post-pass file hash (sha256 of bytes).
15. **Emit external_state.read_back event.** Payload:
    - `task_id`: this branch's ID (T-007.ch-NN).
    - `artifact_url`: file path.
    - `pre_state_ref`: `hash:<pre-pass-sha256>`.
    - `post_state_ref`: `hash:<post-pass-sha256>`.
    - `equality_method`: `file-hash`.
    - `divergence_detected`: true if pre and post hashes are identical (i.e., the edit didn't apply); false if they differ (the expected case).
    - `divergence_notes`: required if divergence_detected is true; describes why the edit didn't land.
16. **Re-render the chapter-source artifact** for the post-split file: hash changes from pre-pass to post-pass; the artifact's `hash` field updates. Add a supersede event chain entry so the prior hash is recoverable.
17. **Update the edit_proposal:** `applied: true`, `applied_at: <ts>`. (The applied flag transition is itself a supersede event for the proposal.)
18. **Branch fold.** Compose a 1-3 sentence summary for the parent T-007 fold result: "ch-NN: <P> passes; final EP-NNN promoted; voice_drift <X>; line_delta <Y>%."
19. Answer @@SCAN markers (the per-branch task carries the SCAN markers; the parent T-007 doesn't repeat them).

## Specific guidance

**Hermetic subagent boundary:** the subagent sees its chapter file + voice anchor + banned-patterns + preservation-rules + philosophy DEC + this chapter's findings/dispositions + summaries-only of prior chapters' edit_proposals. It does NOT see other chapters' full prose, the operator dialog, or any other parts of the run not in `consumes:`. This boundary prevents context bleed and is enforced by the harness's recitation requirement.

**Bounded-iteration cap:** max 3 passes per chapter. If the third pass still doesn't converge, the chapter terminates as `escalated` and the operator decides whether to defer (mark deferred) or take over manually (the operator may directly edit the file outside the harness; the substrate captures that as an external_state.read_back with `equality_method: manual-attestation`).

**Per-chapter cadence:** the operator participates between passes within a chapter (revise directives) and between chapters (promote / move-to-next). This task carries `requires_handoff_acknowledge: true` so a session boundary between chapters resumes cleanly.

**Voice-drift-self-assessment honesty:** understating drift to pass council is a Tier 1 violation. The voice-preservation-watcher cross-checks the self-assessment against the proposal; flagrant under-assessment (subagent says 0.1 but the council sees 0.6) fails council and surfaces as a friction-log entry.

**Scope-shrink awareness:** silently dropping a create_candidate for an `expand` finding (i.e., the subagent saw the finding, decided not to author content for it, and didn't include it in the proposal) is exactly the failure mode scope-shrink-watcher catches. Every finding for this chapter must appear in the proposal as either an edit_candidate, create_candidate, delete_candidate, or an explicit deferral note.

**Live-edit means actuation lands on the file.** This is the marketing-campaign live-edit shape. The pre/post hash check is the structural enforcement that the edit landed.

## Completion Report (filled by executor) (per branch)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** <full list>
- **SCAN markers answered:** <count>
- **Chapter:** ch-NN
- **Pass number:** <P>
- **Pre-pass file hash:** sha256:<...>
- **edit_candidates:** <count>
- **create_candidates:** <count>
- **delete_candidates:** <count>
- **voice_drift_score (self):** <X>
- **line_delta_pct:** <Y>%
- **edit_proposal artifact:** EP-NNN
- **Council verdicts:** voice-preservation=<P/F>, preservation-rule=<P/F>, edit-philosophy-aligner=<P/F>, banned-pattern-enforcer=<P/F>, scope-shrink-watcher=<P/F>
- **Operator decision:** promoted | revised (P+1) | deferred | escalated
- **Post-pass file hash (if actuated):** sha256:<...>
- **external_state.read_back:** EV-NNNN, divergence_detected=<bool>
- **Failure scenarios documented (per elevated risk):** 2
- **Discoveries:** <e.g., "Council failed pass 1 on voice-drift; revised approach with tighter rhythm preservation; pass 2 promoted">
- **Recommended follow-up (next chapter):** ch-(NN+1) or "Phase B complete; T-008 continuity-scan can run."
