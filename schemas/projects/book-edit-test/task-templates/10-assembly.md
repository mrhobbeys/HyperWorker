---
id: T-010
kind: task
schema: book-edit-test
phase: D
risk_level: critical
required_tools: [file_read, file_write, docx_handling]
delivery_mode: live-edit
delivery_mode_fields:
  enumeration_required: false               # one assembly action; not a candidate-enumeration shape
  preview_surface: "schemas/projects/book-edit-test/working/assembly/"
  version_naming: "assembled-manuscript-v{pass}.docx"
  convergence_criterion: "operator approves the assembled manuscript OR three passes elapsed"
  max_passes: 3
requires_handoff_acknowledge: true
depends_on: [T-009]
consumes:
  - "[OR-001#<short-hash>]"
  - "[AM-001#<short-hash>] (assembly map)"
  - "ALL post-edit [SRC-NNN#hash] for post-split-chapter (current state, post-Phase-C)"
  - "ALL applied [EP-NNN#hash]"
  - "ALL Decisions with synthesis_role: continuity-resolution"
acceptance_criteria:
  - "Per-chapter files + front-matter + back-matter are reassembled into a single docx at OR-001.deliverable_path per the AM-001 assembly-map."
  - "Reassembly preserves AM-001's docx_style_inventory: paragraph styles, character styles, fonts, font sizes."
  - "Chapter ordering matches AM-001."
  - "external_state.read_back captures pre-assembly (deliverable_path file hash if it exists, else empty-state ref) and post-assembly file hashes."
  - "The assembled manuscript opens cleanly in a docx reader; section breaks, headings, page-break-before flags preserved."
  - "Council fires (critical risk): voice-preservation-watcher, preservation-rule-watcher, chapter-coverage-auditor, continuity-watcher, operator-goal-aligner all PASS."
---

# Task T-010: Assembly

## Objective

Reassemble the post-edit per-chapter files into a single polished manuscript at `OR-001.deliverable_path`, preserving the docx style inventory and chapter ordering captured in AM-001 at Phase A T-001. The assembly is mechanical (the assembly-map tells us what goes where); the council audit is what makes it a critical-risk task — any drift introduced by the assembly is detectable here, before final-read and print-ready.

## Step-by-Step Instructions

1. Read OR-001 and AM-001 assembly-map.
2. **Confirm all chapters have terminal status.** For each chapter in AM-001, confirm exactly one of:
   - An applied edit_proposal exists (chapter was edited and live-edit landed).
   - An explicit deferral / excluded-after-discovery decision exists for the chapter.
   If neither, flag as a coverage gap and stop. Phase B chapter-coverage-auditor council member should have caught this; if it shows up here, it's a structural failure.
3. **Pre-assembly hash capture.** If `deliverable_path` already exists (from a prior assembly pass), compute its sha256 as `pre_state_ref`. If not, `pre_state_ref: "none"`.
4. **Build the assembled manuscript.** Open a fresh docx workspace. In AM-001's declared chapter order:
   - Append front-matter.docx content (front-matter chapter-source, current state).
   - For each chapter ordinal 01..NN, append the post-split chapter file content (post-split-chapter source, current state).
   - Append back-matter.docx content.
   - Preserve paragraph styles, character styles, font usage, and page-break-before flags per AM-001.docx_style_inventory.
5. **Save the assembled manuscript** to `OR-001.deliverable_path`. Compute post-assembly file hash.
6. **Emit external_state.read_back event.** Payload:
   - `task_id`: T-010.
   - `artifact_url`: deliverable_path.
   - `pre_state_ref`: per step 3.
   - `post_state_ref`: `hash:<post-assembly-sha256>`.
   - `equality_method`: `file-hash`.
   - `divergence_detected`: false (the assembly is expected to produce a different file from any pre-existing one; divergence_detected here means "the file didn't change at all," which would indicate a write failure).
7. **Verify the assembled manuscript opens cleanly.** Open it in a docx reader (or python-docx); confirm no schema errors, no broken section breaks, all chapter headings present in declared order.
8. **Council fires** automatically (per council.yaml triggers for critical-risk task.complete). Members: voice-preservation-watcher, preservation-rule-watcher, chapter-coverage-auditor, continuity-watcher, operator-goal-aligner. Each emits a council.report. Convergence rule: all-agree-or-escalate. If any FAIL, the assembled manuscript is rejected; the failure feeds back into the appropriate prior task (chapter re-pass for voice/preservation failures; T-009 for continuity failures; OR-001 review for operator-goal failures).
9. **Surface to operator.** Brief: deliverable_path, file size, council verdicts, pointer to working assembled-manuscript-v{pass}.docx for the operator to open. Operator confirms: approve | revise | reject. Approve proceeds; revise re-fires upstream; reject defers the project (rare).
10. Answer @@SCAN markers.

## Specific guidance

**Mechanical assembly is not no-judgment assembly.** docx assembly across multiple files involves merging styles definitions, sectionPr handling, and inline-image-ID renumbering. Bugs here are subtle and don't show up in a quick visual check. Use python-docx's composer pattern (or equivalent) and validate the result programmatically: count chapter headings, verify they're in order, sample paragraph styles to confirm they survived.

**Chapter re-pass triggers from council failure:** if voice-preservation-watcher fails on a specific chapter at assembly time (it sees the assembled manuscript and flags drift in chapter X that the per-chapter pass let through), the resolution is to re-fire chapter X's T-007 branch with the assembly-time finding cited. The bounded-iteration cap may need operator-authorized reset.

**Pre-assembly file existence:** if `deliverable_path` exists from a prior pass, the read-back equality_method captures the change. The first assembly pass typically has `pre_state_ref: "none"` since the file doesn't exist yet.

**Assembly is not the polish.** Phase D T-012 final-read is the polish-pass over the assembled manuscript. T-010 is the structural reconstruction; T-012 catches anything the per-chapter passes missed at the document level.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [AM-001#…], [SRC-…], [EP-…], [DEC-…]
- **SCAN markers answered:** <count>
- **Pass number:** <P>
- **Pre-assembly state:** <hash or "none">
- **Post-assembly file:** {{ deliverable_path }}
- **Post-assembly file hash:** sha256:<...>
- **external_state.read_back:** EV-NNNN, divergence_detected=<bool>
- **Chapter ordering verified:** PASS | FAIL (with discrepancies)
- **Style inventory preserved:** PASS | FAIL (with discrepancies)
- **Council verdicts:** voice-preservation=<P/F>, preservation-rule=<P/F>, chapter-coverage-auditor=<P/F>, continuity-watcher=<P/F>, operator-goal-aligner=<P/F>
- **Operator decision:** approved | revised | rejected
- **Failure scenarios documented (per critical risk):** 3
- **Discoveries:** <e.g., "Initial assembly's section breaks landed wrong; corrected on pass 2 by preserving section properties from AM-001 explicitly">
- **Recommended follow-up:** "T-011 voice-guidelines-doc and T-012 final-read can run."
