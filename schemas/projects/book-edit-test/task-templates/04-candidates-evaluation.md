---
id: T-004
kind: task
schema: book-edit-test
phase: A
risk_level: standard
required_tools: [file_read, file_write, docx_handling]
delivery_mode: constrained
depends_on: [T-001]
consumes:
  - "[OR-001#<short-hash>]"
  - "ALL [SRC-NNN#hash] with source_role: candidate-content"
  - "ALL [SRC-NNN#hash] with source_role: post-split-chapter"
acceptance_criteria:
  - "Each candidate-content file is fully read and its content compared against the post-split chapter files."
  - "Per-item disposition: each substantive item in each candidate file is classified as already-incorporated | not-incorporated-fold-in | not-incorporated-discard | not-incorporated-defer."
  - "For 'fold-in' items, the target chapter is identified and the suggested insertion location is captured. The fold-in itself happens during Phase B for the target chapter or as a candidate-disposition Decision authoring a create_candidate."
  - "Each candidate file gets one summary finding (F-NNN with finding_kind: candidate-content-evaluation) plus per-item findings as needed."
  - "An operator-decision Decision is appended (synthesis_role: candidate-disposition) capturing the operator's per-item verdict."
---

# Task T-004: Candidates Evaluation

## Objective

For each file in `OR-001.candidates_folder` (e.g., `notes.docx`, `unused-material.docx`), determine whether the content is already in the manuscript, should be folded in, should be discarded, or should be deferred for later evaluation. The operator makes the final per-item call; this task surfaces the candidates with enough context to decide.

## Step-by-Step Instructions

1. Read OR-001 and the candidate-content artifacts. Read each candidate file's full content.
2. Read the post-split chapter files (or, if memory-bound, read each chapter on-demand as the candidate items are evaluated).
3. **For each candidate file:**
   - Determine the file's nature: pre-writing notes (outline, bullets, scratchpad), unincorporated chapter material (full prose meant for inclusion), or mixed.
   - Walk the candidate file's substantive items (sections, examples, framework descriptions, anecdotes — chunk size depends on the file).
4. **For each substantive item, classify:**
   - **already-incorporated**: the content (or a clear superset) appears in one of the post-split chapters. Note which chapter, with location citation. No action needed.
   - **not-incorporated-fold-in**: the content is in scope (matches book mission, voice-compatible, fits a chapter) and the operator should consider folding it in. Identify the target chapter and a suggested insertion location.
   - **not-incorporated-discard**: the content is out of scope (off-topic, draft-only thinking, contradicts later thinking, voice-incompatible) and should not be folded in.
   - **not-incorporated-defer**: ambiguous; the operator wants to think about it later or decide after seeing chapter passes.
5. **Write a finding artifact for each candidate file's overall evaluation** (`finding_kind: candidate-content-evaluation`) summarizing the file's nature and the count of items per disposition. Per-item findings are written for fold-in candidates (one finding per fold-in item, with the target chapter and insertion location).
6. **Surface to operator.** Present the per-file summary, total fold-in candidates count, total discard count, total defer count. Present the fold-in candidates as a list with their target chapters; operator confirms or revises each.
7. **Append the candidate-disposition Decision.** `synthesis_role: candidate-disposition`. Body: every candidate item listed verbatim with the disposition (already-incorporated | fold-in | discard | defer) and operator-confirmed target chapter for fold-ins.
8. **Fold-in scheduling:** fold-in items become input to the target chapter's Phase B chapter-edit-pass task — the chapter pass `consumes:` the candidate-disposition Decision and may produce a `create_candidate` in its edit_proposal authorized by this Decision.
9. **Move evaluated candidate files** to a sub-folder of candidates_folder named `evaluated/` (e.g., `candidates/evaluated/`). Update the chapter-source artifact for each with a supersede event reflecting the new path. The hash doesn't change (file content unchanged), only `file_path`.
10. Answer @@SCAN markers.

## Specific guidance

**Operator memory:** the operator may not remember each candidate file's intent. The task's job is to surface enough context — a short summary of what the file contains, examples of items inside, comparison against post-split chapters — that the operator can decide quickly.

**Fold-in vs. structural-rewrite:** if a fold-in is large enough that it would push the target chapter past `max_line_delta_pct` even with a substantive-edit philosophy, surface the size as a flag. The operator may then bump the target chapter's edit philosophy to `structural-rewrite` or accept that the fold-in pushes the line-delta cap (per-chapter override DEC).

**Voice compatibility check:** a fold-in candidate that doesn't match VA-001's voice should be flagged. The operator may decide to fold-in-and-rewrite (which becomes a substantive-edit pass for the target chapter) or to discard.

**Discard reasoning is captured.** The candidate-disposition Decision body records why each discard was a discard, so future runs (or the saved book-edit schema) can learn from the pattern.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [SRC-…] for candidates and chapters
- **SCAN markers answered:** <count>
- **Candidate files evaluated:** <count>
- **Total items classified:**
  - already-incorporated: <count>
  - fold-in (operator-approved): <count>
  - discard (operator-approved): <count>
  - defer: <count>
- **Per-file findings:** F-NNN through F-MMM
- **Per-fold-in findings:** F-NNN through F-MMM
- **candidate-disposition Decision:** DEC-NNN
- **Files moved to evaluated/:** <list>
- **Discoveries:** <e.g., "unused-material.docx contains three items already in chapter 6 and one item that's a clear fold-in for chapter 9">
- **Recommended follow-up:** "Phase B chapter passes for any chapter with fold-in items will consume DEC-NNN; T-005 unfinished-bits-scan can run next (or in parallel with this task)."
