---
id: T-006
kind: task
schema: book-edit-test
phase: A
risk_level: standard
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: [T-002, T-005]
lightweight_completion: true
consumes:
  - "[OR-001#<short-hash>]"
  - "[VA-001#<short-hash>]"
  - "ALL F-NNN with finding_kind: unfinished-bit | placeholder-marker | incomplete-sentence | broken-internal-reference (per chapter)"
  - "ALL F-NNN with finding_kind: candidate-content-evaluation that flagged a target chapter for fold-in"
acceptance_criteria:
  - "Each chapter (and front-matter, back-matter) has an explicit edit-philosophy declaration: light-copyedit | substantive-edit | structural-rewrite. Default per OR-001.edit_philosophy_default unless the operator overrides for this chapter."
  - "Per-chapter override Decisions (DEC-NNN, synthesis_role: chapter-edit-philosophy, chapter_scope: ch-NN) are appended for any chapter that deviates from default."
  - "Per-chapter max_line_delta_pct override (if any) is captured in the same Decision."
  - "Per-chapter disposition rationale: if a chapter's philosophy is bumped to substantive or structural, the rationale cites the relevant findings (e.g., 'ch-07 bumped to substantive because 6 unfinished-bit findings + 1 fold-in candidate-content item exceed the light-copyedit envelope')."
---

# Task T-006: Edit Philosophy Per Chapter

## Objective

Operator declares the edit philosophy for each chapter. Default philosophy comes from `OR-001.edit_philosophy_default` (typically `light-copyedit`); chapters that need more (because of fold-ins, substantial unfinished bits, or operator preference) get explicit overrides captured as Decisions. The Phase B chapter-edit-pass for each chapter `consumes:` the chapter's philosophy Decision to know what envelope to operate within.

## Step-by-Step Instructions

1. Read OR-001 and VA-001 voice-anchor.
2. **For each chapter** (and front-matter, back-matter), gather signal:
   - Count of unfinished-bit findings with disposition `expand` (these add work to the chapter; bias toward substantive).
   - Count of unfinished-bit findings with disposition `cut` (these reduce work; consistent with light-copyedit).
   - Count of candidate-content fold-in items targeting this chapter (these add content; bias toward substantive or structural).
   - Operator's expressed preference, if any (some chapters the operator may already know need restructuring — they tell us at bootstrap or here).
3. **Surface signal to operator chapter-by-chapter** with a recommended philosophy:
   - `light-copyedit` if: spelling/grammar + banned-pattern removal + small unfinished-bit handling fits within max_line_delta_pct.
   - `substantive-edit` if: fold-ins or expand-disposition unfinished bits push beyond a copyedit envelope, but chapter structure stays.
   - `structural-rewrite` if: chapter structure itself needs revisiting (large fold-ins, multiple expand bits, operator-flagged structural issues).
4. **Operator confirms or overrides** per chapter. For each override:
   - `synthesis_role: chapter-edit-philosophy`.
   - `chapter_scope: ch-NN`.
   - Body: declared philosophy, rationale (with citations to specific findings), and any per-chapter `max_line_delta_pct` override.
   - Run `hw add decision < draft.md`.
5. For chapters using the default, no Decision is required (the default flows from OR-001). The completion report records the default-vs-override breakdown.
6. Answer @@SCAN markers.

## Specific guidance

**Default is the default.** Don't over-declare overrides. If a chapter has no fold-ins, no expand-disposition findings, and no operator concern, it stays at the default; that's not a Decision worth writing.

**Override decisions cite specific findings.** "ch-07 bumped to substantive-edit because: 6 unfinished-bit findings (F-021..F-026) with expand dispositions, plus 1 candidate-content fold-in (F-031); estimated line-delta 45-55% exceeds default 30% cap" is a useful rationale. "ch-07 needs more work" is not.

**max_line_delta_pct overrides** are quiet. If you're confident a chapter will exceed the cap and the operator's authorized that, raise the cap in the same Decision rather than failing Layer 2 mid-pass and re-running.

**Front matter and back matter philosophy** is typically light-copyedit (correcting copyright dates, dedication, also-by, about-author bio). If the operator wants substantive front-matter rewriting (e.g., new foreword, new introduction), flag as a structural-rewrite override.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [VA-001#…], [F-…] for relevant findings
- **SCAN markers answered:** <count>
- **Chapters total:** <N>
- **Default-philosophy chapters:** <count>
- **Overridden chapters:** <count, with chapter_id → philosophy>
- **chapter-edit-philosophy Decisions appended:** DEC-NNN through DEC-MMM
- **max_line_delta_pct overrides:** <list of chapter → cap>
- **Discoveries:** <e.g., "ch-09 had no findings of any kind; pure light-copyedit candidate; ch-07 has the most signal across all categories">
- **Recommended follow-up:** "Phase B can begin. Each chapter-edit-pass branch will consume its chapter's philosophy DEC (or the project default if no override)."
