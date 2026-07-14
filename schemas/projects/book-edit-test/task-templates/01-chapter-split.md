---
id: T-001
kind: task
schema: book-edit-test
phase: A
risk_level: standard
required_tools: [file_read, file_write, docx_handling]
delivery_mode: constrained
depends_on: [T-000]
consumes:
  - "[OR-001#<short-hash>]"
  - "[SRC-NNN#<short-hash>] (the canonical manuscript)"
acceptance_criteria:
  - "Source manuscript opened and chapter boundaries identified by paragraph style / heading / page-break analysis. Boundary detection method documented."
  - "Each chapter is written to a separate .docx file in OR-001.input_folder; filename follows the convention chapter-NN.docx where NN is zero-padded chapter ordinal."
  - "Each per-chapter file is registered as a chapter-source artifact with source_role: post-split-chapter and chapter_id: ch-NN."
  - "An assembly-map artifact (AM-001) is created recording: chapter_id → original_paragraph_range, original heading text and style, post_split_file citation, front_matter and back_matter regions, and a docx_style_inventory."
  - "Front matter (title page, copyright, dedication, TOC) and back matter (about author, also-by) are extracted to separate files (front-matter.docx, back-matter.docx) and registered with source_role: post-split-chapter and chapter_id: front-matter | back-matter."
  - "Reassembling per-chapter files + front matter + back matter using the assembly-map produces a manuscript byte-equivalent (modulo internal docx XML normalization) to the canonical manuscript at this point."
---

# Task T-001: Chapter Split

## Objective

Open the canonical manuscript, identify chapter boundaries, write each chapter to its own .docx file in `OR-001.input_folder`, and capture an assembly-map artifact that records exactly how the manuscript was decomposed so Phase D T-010 can reassemble byte-faithfully.

This task is the structural precondition for Phase B's per-chapter atomic editing. Without per-chapter files, the chapter-edit-pass subagents cannot be hermetic.

## Step-by-Step Instructions

1. Read OR-001 and the canonical manuscript chapter-source artifact.
2. **Open the canonical manuscript .docx file.** Use python-docx (or equivalent) to walk the document's paragraphs in order. For each paragraph, record: paragraph index, style name (e.g., "Heading 1", "Body Text"), text content (first 80 chars for logging), and any explicit page-break-before flag.
3. **Identify chapter boundaries** using a layered heuristic:
   - Primary: paragraph style is "Heading 1" (or equivalent top-level heading style declared in the docx).
   - Secondary: text content matches `^(Chapter|CHAPTER)\s+\d+` or matches a known chapter-title pattern.
   - Tertiary: explicit page-break-before flags adjacent to bold-large-text paragraphs (manual page-break + heading-styled-as-body pattern).
   - Document the detection method actually used in the completion report. If multiple methods are needed, document each.
4. **Identify front matter and back matter** boundaries:
   - Front matter: paragraphs before the first chapter heading. Typically title page, copyright, dedication, TOC.
   - Back matter: paragraphs after the last chapter's content. Typically about-author, also-by, acknowledgments.
5. **Build the chapter index.** A list of `{chapter_id, ordinal, title, paragraph_start, paragraph_end, heading_style, post_split_file_path}`. The first chapter is `ch-01`, the second `ch-02`, etc. The chapter title is the text of the heading paragraph.
6. **Write per-chapter files.** For each chapter, create a new .docx file at `{input_folder}/chapter-NN.docx`. Copy the chapter's paragraphs (including the heading) into the new file, preserving paragraph styles, character formatting, embedded images, tables, footnotes, and any explicit page-break-before flags. Confirm the new file opens cleanly in a docx reader (no schema errors).
7. **Write front-matter and back-matter files** to `{input_folder}/front-matter.docx` and `{input_folder}/back-matter.docx` with the same fidelity.
8. **Register each post-split file as a chapter-source artifact.** `source_role: post-split-chapter`, `round: post-split`, `weight: primary` (these are now the source-of-truth for live edits), `chapter_id: ch-NN | front-matter | back-matter`, `supersedes: [SRC-canonical-manuscript#hash]` (the post-split chapters supersede the manuscript-grain canonical for editing purposes; the manuscript itself remains the historical original).
9. **Build the docx_style_inventory.** A catalog of paragraph styles, character styles, fonts used, font sizes, and any custom style definitions. Phase E print-ready formatting consumes this to preserve the visual identity in layout.
10. **Write the assembly-map artifact** AM-001. Run `hw add assembly-map < draft.md`.
11. **Verify reassembly.** Compose a temporary reassembled docx from the per-chapter files + front-matter + back-matter using the assembly-map, then byte-compare (or XML-normalize-then-compare) against the canonical manuscript. Confirm equivalence. Document any discrepancies (typically: docx normalization differences in IDs, sectionPr ordering, inline image hashes — these are acceptable; substantive content differences are not). Discard the temporary file once equivalence is confirmed.
12. Answer @@SCAN markers.

## Specific guidance

**Boundary detection failure modes:** the source manuscript was assembled quickly and may have inconsistent heading styles. If the primary heuristic (Heading 1) misses chapters or over-captures (e.g., catches a sub-heading), document the false positives/negatives and surface for operator review BEFORE writing per-chapter files. Splitting against wrong boundaries pollutes Phase B; the cost of a five-minute operator confirmation is low compared to the cost of redoing 10 chapter passes.

**Chapter count vs. T-000 estimate:** the bootstrap probe estimated chapter count from the canonical manuscript; T-001's actual count should match within ±1. A larger gap indicates a structural issue worth surfacing.

**Embedded images / tables / footnotes:** copy them faithfully. python-docx supports paragraph-level copy via XML element duplication; use that path rather than text-only copy. The fidelity bar for chapter-split is byte-equivalent reassembly; lossy splits are unacceptable.

**Manuscript with no heading styles:** if the canonical manuscript was authored without paragraph styles (rare but possible — fully-flat docx with manual formatting), boundary detection falls back to the secondary/tertiary heuristics. Document this in the completion report and surface for operator confirmation; the friction log entry is automatic.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [SRC-canonical-manuscript#…]
- **SCAN markers answered:** <count>
- **Boundary detection method:** primary | secondary | tertiary | mixed (with details)
- **Chapter count:** <N>
- **Chapters identified:** ch-01 through ch-NN with titles
- **Front matter detected:** <yes/no, paragraph range>
- **Back matter detected:** <yes/no, paragraph range>
- **Post-split files written:** <count>
- **chapter-source artifacts registered:** SRC-NNN through SRC-MMM (post-split-chapter)
- **Assembly map:** AM-001
- **Reassembly verification:** PASS (byte-equivalent) | PASS (XML-normalized-equivalent) | FAIL (with documented diff)
- **Discoveries:** <e.g., "Two chapters share Heading 1 style but a sub-section heading also got Heading 1; corrected during boundary detection — flagged as F-NNN for operator awareness">
- **Recommended follow-up:** "T-002 voice-anchor-extraction can run next; per-chapter files are the source-of-truth input."
