---
id: T-000
kind: task
schema: book-edit-test
phase: A
risk_level: standard
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: []
consumes:
  - "[OR-001#<short-hash>]"
  - "bootstrap.scope_locked event payload"
acceptance_criteria:
  - "Every file in OR-001.source_manuscript_path, OR-001.input_folder, OR-001.archive_folders, and OR-001.candidates_folder is registered as a chapter-source artifact OR explicitly noted in the completion report as not-a-source (e.g., README, .gitignore) with reason."
  - "Each chapter-source has source_role, round, weight, and hash populated."
  - "Round chains across archive files are linked: supersedes/superseded_by populated where filename or content reveals a round relationship (Unformatted → Formatted V1 → V2 → Edited → Completed)."
  - "Duplicate-by-hash files are collapsed: two files with byte-identical content register as one chapter-source artifact; duplicates noted in completion report."
  - "Banned tokens table and Canonical facts table in 00-REFERENCE-rules.md are populated (or explicitly marked empty for the operator's confirmation)."
---

# Task T-000: Corpus Inventory

## Objective

Catalog every file in the project's declared folders as a `chapter-source` artifact. Establish round relationships between archive files where filename conventions reveal them. Register the canonical manuscript explicitly with `source_role: canonical-manuscript` (the file Phase A T-001 will split). Lock canonical facts and banned-pattern seed entries in `00-REFERENCE-rules.md` so downstream tasks can reference them.

The bootstrap inventory sweep already produced a verified file list via `bootstrap.scope_locked`. T-000 inherits that list and registers each file as a typed artifact, adding the SHA-256 deduplication pass and the round-chain inference.

## Step-by-Step Instructions

1. Read OR-001. Note `source_manuscript_path`, `input_folder`, `archive_folders`, `candidates_folder`, `banned_patterns_seed`.
2. Read the locked scope from `bootstrap.scope_locked` (the most recent event of that kind for this project).
3. **Compute SHA-256 of every file in scope** before registration. Two files with byte-identical content register as one chapter-source artifact; the duplicate filename is noted in the completion report.
4. **Register the canonical manuscript** explicitly: `source_role: canonical-manuscript`, `round: completed`, `weight: primary`, `chapter_id: null` (the manuscript spans all chapters), `supersedes`: link to any earlier round files this manuscript supersedes (typically all the archive-original files).
5. **Register each archive-original file:** `source_role: archive-original`, `round: unformatted | formatted-v1 | formatted-v2`, `weight: secondary`, `chapter_id`: derived from filename if a single chapter is in the file (else null), `supersedes`: link to earlier round if naming convention reveals it.
6. **Register each archive-edited file:** `source_role: archive-edited`, `round: edited`, `weight: secondary`, `chapter_id`: derived from filename, `supersedes`: link to the corresponding archive-original chapter file if clear, `superseded_by`: link to canonical manuscript SRC-ID once that's registered.
7. **Register each candidate-content file:** `source_role: candidate-content`, `round: candidate`, `weight: contextual`, `chapter_id: null`. Content disposition is determined later by T-004 candidates-evaluation.
8. After all `chapter-source` artifacts are registered, update `superseded_by` on older rounds (per SUBSTRATE.md §Superseded Artifact Back-Link).
9. **Banned-pattern seed registration.** For each item in OR-001.banned_patterns_seed (default ["em dash"]), write a banned-pattern artifact with `source: operator-direct`, `confidence: validated`. Run `hw add banned-pattern < draft.md` per substrate protocol. The em-dash artifact's `pattern` is the literal Unicode em dash character; `pattern_kind: unicode-codepoint`; `pattern_class: punctuation`; `replacement_rule: "em dash → parentheses for parenthetical scope, ellipsis for trailing thought, comma for in-line clause (operator preference)"`.
10. **Canonical-facts seeding.** Populate the Canonical facts table in `00-REFERENCE-rules.md` with at minimum: book title, book short title, book platform ID (ISBN/ASIN/etc.), book listing URL (from OR-001.book_metadata). Add any operator-declared brand/product/framework names known at this stage.
11. Answer @@SCAN markers from `00-REFERENCE-rules.md`.

## What this task is NOT

Not chapter-content extraction. Reading chapter content is T-002 (voice anchor) and T-005 (unfinished bits) and T-007 (per-chapter passes). T-000 reads filenames and a quick scan of the first 20 lines of each file (only enough to confirm `source_role` and `chapter_id` heuristics). Full content reads happen in later tasks.

Not chapter splitting. The canonical manuscript is registered as one artifact in T-000; T-001 (chapter-split) does the per-chapter file creation and writes the assembly-map artifact.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…]
- **SCAN markers answered:** <count>
- **chapter-source artifacts registered:** SRC-001 through SRC-NNN
- **Canonical manuscript registered as:** SRC-NNN with role canonical-manuscript
- **Archive-original files registered:** <count>
- **Archive-edited files registered:** <count>
- **Candidate-content files registered:** <count>
- **Round chains identified:** <list of supersedes chains, e.g., "Chapter 1 Draft V2 → Chapter 1 Edited → (chapter 1 region of the canonical manuscript)">
- **Duplicate-by-hash files collapsed:** <list>
- **Banned-pattern seed artifacts registered:** BP-001 through BP-NNN
- **Canonical facts seeded:** <list>
- **Discoveries:** <e.g., "Chapter 10 Draft V1.docx exists but no V2; chain ends at V1 for that chapter">
- **Recommended follow-up:** "T-001 chapter-split should run next; canonical manuscript is the source-of-truth input."
