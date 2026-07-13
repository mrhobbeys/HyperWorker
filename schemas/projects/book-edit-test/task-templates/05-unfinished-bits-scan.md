---
id: T-005
kind: task
schema: book-edit-test
phase: A
risk_level: standard
required_tools: [file_read, file_write, docx_handling]
delivery_mode: constrained
depends_on: [T-001]
consumes:
  - "[OR-001#<short-hash>]"
  - "ALL [SRC-NNN#hash] with source_role: post-split-chapter"
acceptance_criteria:
  - "Every post-split chapter file (including front-matter and back-matter) has been fully read."
  - "Every signal of unfinished work is captured as a finding artifact: placeholder markers (TK, TBD, [bracket notes], (expand here), 'come back to this'), incomplete sentences, paragraphs that trail off, internal references to chapters/sections that don't exist or aren't substantively present, missing examples ('we'll see an example of this — TBD')."
  - "Each finding has finding_kind in {unfinished-bit, placeholder-marker, incomplete-sentence, broken-internal-reference, ai-indicator-candidate}, chapter_id, and location."
  - "Per-finding operator disposition: leave (acknowledge as intentional), expand (operator wants content authored), cut (operator wants the surrounding context removed). Captured as one Decision (synthesis_role: unfinished-bit-disposition) per finding OR aggregated into one Decision per chapter."
  - "Findings for 'expand' dispositions describe what content would fill the gap (operator may provide directly or note 'subagent should propose during Phase B chapter pass')."
---

# Task T-005: Unfinished Bits Scan

## Objective

Walk every post-split chapter and surface signals of unfinished work the author left mid-draft. The author noted at bootstrap that the original was written under challenge-group time pressure and contains unfinished bits — placeholders the author intended to come back to. Each finding gets an operator disposition (leave / expand / cut) before Phase B chapter passes begin so the per-chapter passes know what to do with each placeholder.

## Step-by-Step Instructions

1. Read OR-001.
2. **For each post-split chapter file** (ch-NN.docx and front-matter.docx and back-matter.docx):
   - Open the file, walk paragraphs in order.
   - Scan for **explicit placeholder markers**: `TK`, `TBD`, `XXX`, `[insert ...]`, `[expand]`, `(come back to this)`, `(check this)`, `(verify)`, `[CITATION NEEDED]`, `???`, parenthetical author-notes-to-self that read as "I need to do X here later."
   - Scan for **incomplete sentences**: sentences ending mid-clause without terminating punctuation, sentences ending in dangling conjunctions or prepositions.
   - Scan for **paragraphs that trail off**: ellipses-trailing paragraphs, very short paragraphs at section ends that read as "I'll write more here," paragraphs that introduce a list with no list following.
   - Scan for **internal references to nothing**: "as we saw earlier", "we'll see in chapter N", "the X framework discussed above" — verify each resolves to actual content. References that don't resolve are findings.
   - Scan for **missing examples**: "for example, ..." with no example following, "consider this scenario: TBD", explicit "[example needed]" markers.
   - Scan for **AI-indicator-suspect content** that wasn't operator-authored: if a paragraph reads as boilerplate or as having drifted in style from the surrounding chapter, flag as `ai-indicator-candidate` for operator review (this is heuristic; false positives are expected and cheaper than false negatives).
3. **Write a finding artifact for each signal.** Each finding:
   - `finding_kind`: per the enum.
   - `chapter_id`: the chapter where the signal appears.
   - `location`: paragraph index + a short excerpt for context (3 sentences before, the marker, 3 sentences after — or the full paragraph if shorter).
   - `from_source`: citation to the chapter source artifact.
   - Body: a brief description of what the signal looks like and why it's flagged.
4. **Surface findings to operator** chapter-by-chapter (not all-at-once if the count is high). Format:
   - Per chapter: count of findings by kind, with one-line excerpts.
   - Operator disposition per finding: leave | expand | cut. For expand dispositions, the operator either provides the content directly (captured in the disposition Decision) or notes "subagent proposes during Phase B chapter pass" (the chapter pass's edit_proposal will include a create_candidate authorized by the disposition Decision).
5. **Append unfinished-bit-disposition Decisions.** Either one Decision per finding (high resolution, more events) or one Decision per chapter aggregating that chapter's dispositions (lower resolution, fewer events). Default: aggregate per chapter unless a single finding has substantial operator-supplied expand content (which would bloat the chapter-aggregate Decision).
6. **Cross-link to T-007 chapter-edit-pass:** for each chapter, the chapter's edit-pass task `consumes:` the unfinished-bit-disposition Decision(s) for that chapter. The chapter pass uses the disposition to decide whether to author content (expand), remove (cut), or preserve as-is (leave) for each finding's location.
7. Answer @@SCAN markers.

## Specific guidance

**False positives are cheap; false negatives are expensive.** A scan that flags 15 candidates of which 5 turn out to be intentional author choices (and the operator marks "leave") is a successful scan. A scan that misses 2 unfinished bits is a failure that bites in Phase D final-read.

**The operator's working memory is finite.** Surface findings chapter-by-chapter, not as one giant list. The chapter-by-chapter cadence aligns with the per-chapter operator review cadence in Phase B and lets the operator stay in context.

**Internal-reference resolution is structural.** A "see chapter 7" reference is a resolvable claim: chapter 7 must exist and must contain content the reference is about. The scan checks both halves; missing chapter and missing content are both broken-internal-reference findings.

**Front matter and back matter need scanning too.** Title pages with `[insert dedication here]` placeholders, copyright pages with `[year]` placeholders, also-by lists with `[other titles]` are common. Scan with the same rigor.

**AI-indicator-suspect content from a draft is worth flagging.** If the operator used AI assistance during the original draft and some paragraphs slipped through, this scan is the structural place to surface them. The operator decides: keep (and presumably tighten via banned-pattern enforcement in Phase B), expand (rewrite), or cut.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [SRC-…] for each chapter
- **SCAN markers answered:** <count>
- **Chapters scanned:** <list of chapter_ids>
- **Findings produced:** F-NNN through F-MMM (with per-kind counts)
  - placeholder-marker: <count>
  - incomplete-sentence: <count>
  - broken-internal-reference: <count>
  - ai-indicator-candidate: <count>
  - unfinished-bit (other): <count>
- **unfinished-bit-disposition Decisions appended:** DEC-NNN through DEC-MMM
- **Operator dispositions:**
  - leave: <count>
  - expand: <count>
  - cut: <count>
- **Discoveries:** <e.g., "Chapter 7 has six 'come back to this' markers; chapter 9 has none — uneven completion across the book confirms the challenge-group time-pressure pattern operator described">
- **Recommended follow-up:** "T-006 edit-philosophy-per-chapter can run next; per-chapter passes T-007 will consume the dispositions for their chapter."
