---
id: T-013
kind: task
schema: book-edit-test
phase: E
risk_level: critical
required_tools: [file_read, file_write, docx_handling, pdf_render]
delivery_mode: live-edit
delivery_mode_fields:
  enumeration_required: false
  preview_surface: "schemas/projects/book-edit-test/working/print-ready/"
  version_naming: "print-ready-v{pass}.docx"
  convergence_criterion: "operator approves the print-ready manuscript OR three passes elapsed"
  max_passes: 3
requires_handoff_acknowledge: true
depends_on: [T-012]
consumes:
  - "[OR-001#<short-hash>]"
  - "[AM-001#<short-hash>] (assembly map for style inventory)"
  - "Final manuscript at OR-001.deliverable_path"
  - "Operator-supplied print specs (trim size, margins, font, design preferences) — captured as a Decision at task start"
acceptance_criteria:
  - "Operator-supplied print specs are captured as a Decision (DEC-NNN, synthesis_role: scope-decision, body: trim_size, margins, font_family/size, header/footer rules, design preferences) before any layout work begins."
  - "Trim size set per spec (typical: 5x8, 6x9, 5.5x8.5)."
  - "Margins set per spec (typical: inside 0.875 in, outside 0.625 in for POD; or operator-declared)."
  - "Page numbers added per spec (typical: bottom-center starting at first chapter; roman numerals for front matter)."
  - "Headers/footers set per spec (typical: book title left page, chapter title right page; or operator-declared)."
  - "Front matter laid out: title page, copyright (with current year and ISBN if supplied), dedication, TOC."
  - "Back matter laid out: about author, also-by, acknowledgments per supplied content."
  - "Chapter heading styling: consistent across chapters per AM-001 docx_style_inventory + spec overrides."
  - "Widow/orphan control set; no chapter starts mid-page."
  - "Image resolution check: any embedded images pass 300 DPI for print (or operator confirms lower acceptable)."
  - "Output written to OR-001.print_ready_path. external_state.read_back captures pre/post hashes."
  - "Council fires (critical risk); all members PASS."
---

# Task T-013: Print-Ready Formatting

## Objective

Take the polished content manuscript at `OR-001.deliverable_path` and produce a print-ready laid-out version at `OR-001.print_ready_path` suitable for POD print pipelines (KDP Print, IngramSpark) or operator-declared specifications. The substantive content does not change in this task — only layout, typography, and document structure.

## Step-by-Step Instructions

1. Read OR-001 and AM-001.
2. **Capture operator print specs.** Ask the operator (or load from a pre-supplied specs file):
   - Trim size (e.g., 5x8, 6x9, 5.5x8.5).
   - Margins (inside, outside, top, bottom). Default for POD: 0.875 inside, 0.625 outside, 0.75 top/bottom.
   - Font family and size (typical: 11pt or 12pt serif body; sans-serif headings).
   - Header / footer rules.
   - Page numbering convention (start page, roman numerals for front matter, etc.).
   - Front matter content (title page, copyright text, dedication, TOC scope).
   - Back matter content (about author, also-by, acknowledgments).
   - Any design preferences (drop caps? scene-break ornaments? running heads? chapter-opener treatments?).
   - ISBN (if available).
   - Image resolution requirements (300 DPI typical for print).
   Capture the answers as a Decision artifact (`synthesis_role: scope-decision`, body: full spec). The DEC is consumed by the rest of this task.
3. **Apply trim size and margins** to the working copy. python-docx-section properties or equivalent.
4. **Set headers and footers** per spec.
5. **Add page numbers** per convention. Front matter typically gets lowercase roman numerals; the body starts page 1 at the first chapter.
6. **Lay out front matter:**
   - Title page (book title + author).
   - Copyright page (copyright text, current year, ISBN if available, "all rights reserved" or chosen license, edition note if re-release: "Second Edition" or "Revised Edition").
   - Dedication (if supplied).
   - Table of Contents (auto-generated from chapter headings).
7. **Lay out chapter headings** per AM-001 docx_style_inventory + any operator overrides. Consistent across all chapters.
8. **Set widow/orphan control.** No chapter ends with a single line on a page; no chapter starts with a single line on a page; no paragraph has a single line on either side of a page break.
9. **Chapter starts on right-hand page** (recto) per print convention, unless operator overrides.
10. **Image resolution check.** Walk all embedded images; flag any below 300 DPI. Operator confirms whether to swap (typical: replace with higher-resolution source) or accept lower.
11. **Lay out back matter:**
    - About the author.
    - Also-by (other works).
    - Acknowledgments (if supplied).
12. **Save to OR-001.print_ready_path.** Compute pre and post file hashes; emit external_state.read_back per live-edit primitive.
13. **Render a sample PDF** at the declared trim size for visual review. (PDF rendering uses the docx_handling tool's PDF export, or a separate pdf_render tool.) Save sample to working/print-ready/sample-v{pass}.pdf for operator visual review.
14. **Surface to operator.** Brief: print_ready_path, sample PDF path, dimensions confirmed (trim size + page count), front/back matter confirmed, image resolution check result. Operator opens the sample PDF and confirms: approve | revise | reject.
15. **Council fires** (critical risk per council.yaml). Members assess document-level integrity (chapter ordering preserved, content unchanged from T-010 except in layout).
16. Answer @@SCAN markers.

## Specific guidance

**Content does not change.** This task is layout-only. If a content-level fix is identified during print-ready (e.g., a chapter-opener page number floats wrong because of a mid-paragraph hard break), the fix routes back to T-010 (assembly) or T-012 (final-read) — not patched in T-013. Layout failures that reveal content issues are friction-log signal.

**Trim-size + margin = page count.** Operator typically has a target page count (e.g., POD pricing tier breaks at certain page counts). The trim/margin/font-size combination determines page count. If the result misses the target by enough to matter, surface and let operator decide trade-offs (smaller font + more margin? bigger trim?).

**Image-resolution check is a real check.** Self-published books often ship with low-resolution images that look fine on Kindle and bad in print. The 300 DPI bar is the print standard. The operator may accept lower (a screenshot can be 96 DPI and still legible) but the choice should be explicit.

**ISBN may not be available.** If the print release uses a new ISBN, it may be assigned by the POD service after the file is uploaded. Leave a placeholder (`ISBN: [pending]`) and document in the completion report; the operator updates the copyright page after assignment.

**PDF sample render is critical.** Docx is not WYSIWYG for print at the trim-size scale. The PDF render is the operator's actual review surface; if the docx looks fine and the PDF doesn't, the PDF is right.

**Print-ready vs ebook.** This task targets print. The polished manuscript at deliverable_path is the source for both print (T-013 output) and a Kindle update (post-archive backlog item — separate task, separate file path; the Kindle update reflows to device, which is a different layout problem). T-013 does not produce the Kindle file.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [AM-001#…], [DEC-…] (print specs)
- **SCAN markers answered:** <count>
- **Pass number:** <P>
- **Print specs Decision:** DEC-NNN
- **Trim size:** <e.g., 6x9>
- **Total page count:** <N>
- **Pre-print-ready file hash:** sha256:<...> (deliverable_path)
- **Post-print-ready file hash:** sha256:<...> (print_ready_path)
- **Sample PDF:** working/print-ready/sample-v{pass}.pdf
- **external_state.read_back:** EV-NNNN
- **Image resolution check:** all-pass | <count below 300 DPI, with operator's per-image disposition>
- **Council verdicts:** <one line per member>
- **Operator decision:** approved | revised | rejected
- **Failure scenarios documented (per critical risk):** 3
- **Discoveries:** <e.g., "Sample PDF revealed chapter-opener treatment looked sparse at 6x9; operator opted for drop-cap on first paragraph">
- **Recommended follow-up:** "Project ready for hw wrap; post-archive backlog includes Amazon listing update for {{ book_short_title }}."
