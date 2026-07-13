---
id: T-002
kind: task
schema: book-edit-test
phase: A
risk_level: standard
required_tools: [file_read, file_write, docx_handling]
delivery_mode: constrained
depends_on: [T-001]
consumes:
  - "[OR-001#<short-hash>]"
  - "[AM-001#<short-hash>] (assembly map)"
  - "ALL [SRC-NNN#hash] with source_role: post-split-chapter"
acceptance_criteria:
  - "voice-anchor artifact (VA-001) is created with: at least 5 sample_excerpts spanning at least 3 different chapters (representativeness check), tone_descriptors populated, sentence_rhythm_notes populated, vocabulary_register populated, voice_dont_list populated (or explicitly empty []), and operator_overrides populated from OR-001."
  - "Each sample_excerpt cites a post-split-chapter source by hash and includes a 'why_representative' note."
  - "operator_overrides include the em-dash → parentheses/ellipsis rule from OR-001.banned_patterns_seed and any other explicit operator-supplied voice rules."
  - "If OR-001.voice_anchor_strategy is operator-supplied or mixed, operator-supplied excerpts (if any) are integrated into sample_excerpts."
---

# Task T-002: Voice Anchor Extraction

## Objective

Extract a voice-anchor artifact from representative passages of the post-split chapter files. The voice-anchor is consumed by every Phase B chapter pass and by every council fire that includes voice-preservation-watcher. It must be substantive enough that a hermetic subagent can use it to evaluate whether a proposed edit drifts from the author's voice.

## Step-by-Step Instructions

1. Read OR-001. Note `voice_anchor_strategy`, `banned_patterns_seed`, and any operator-supplied voice excerpts captured during bootstrap.
2. Read the assembly-map AM-001 to get the chapter list.
3. **Sample chapters for representativeness.** Pick at least 3 chapters that span the book's range (early, middle, late). Skip front matter and back matter — the voice anchor is for the substantive prose.
4. **For each sampled chapter, read the chapter file.** Identify 1-2 representative passages per chapter, prioritizing:
   - Passages with the author's characteristic sentence rhythm (parenthetical asides, ellipsis trails, list-of-three patterns the author uses).
   - Passages with the author's vocabulary register signature (technical-but-accessible lexicon, first-person plural shifts, idiomatic phrasings).
   - Passages where the author uses real examples or anecdotes (these become preservation rule references too).
5. **Build the voice-anchor artifact** VA-001 with:
   - `sample_excerpts`: list of `{source_citation, chapter_id, excerpt_text, why_representative}`. At least 5 entries, spanning at least 3 chapters.
   - `tone_descriptors`: list of adjectives/short phrases describing the voice (e.g., "pragmatic-not-academic", "first-person-plural-occasionally", "examples-driven", "asks-the-reader-questions").
   - `sentence_rhythm_notes`: prose describing observed patterns. Sentence length distribution. Parenthetical-vs-comma habits. Paragraph cadence (short-short-long? long-establishing then short-punctuating?). The operator's stated preference for parentheses and ellipses over em dash goes here too.
   - `vocabulary_register`: prose describing the lexical level. Technical terms used without definition? Casual register? Direct addressing of reader? Specific verbs / nouns the author returns to?
   - `voice_dont_list`: phrasings or rhetorical moves the author's voice clearly avoids. Heuristic: if a phrasing would feel out of place inserted into a sample passage, add it here. Empty list `[]` if none observed (not null).
   - `operator_overrides`: list of operator-declared rules. At minimum: "em dash is banned; replacement rule per OR-001.banned_patterns_seed (parentheses for parenthetical scope, ellipsis for trailing thought, comma for in-line clause)." Plus any other explicit voice rules the operator captured at bootstrap.
6. Run `hw add voice-anchor < draft.md` per substrate protocol.
7. **Update 00-REFERENCE-rules.md Tier 4 STYLE** to cite VA-001 as the canonical voice reference. The Tier 4 section gets a short pointer ("Voice anchor: [VA-001#hash]; consumed by every chapter pass") rather than the full anchor content.
8. Answer @@SCAN markers.

## Specific guidance

**Do not over-fit to one chapter.** The voice should sample across the book. Front matter and back matter often have a different register (more formal in title page text, more casual in dedications) and are excluded.

**Do not paraphrase the author's voice in tone_descriptors.** "Pragmatic-not-academic" is a tag; "the author writes in a way that's pragmatic and avoids academic language" is paraphrase. Tags are easier for council members to compare against proposed edits.

**Capture the don't-list explicitly.** Empty void of "this isn't the voice" markers is the failure mode where voice-preservation-watcher passes any edit because nothing it sees matches the don't-list. If genuinely nothing is observable, write `voice_dont_list: []` and explain in the artifact body what was looked for.

**Operator-supplied excerpts:** if the operator dropped specific sample passages at bootstrap, they MUST be included in sample_excerpts (highest priority). If the operator declared rules verbatim, they go in operator_overrides verbatim.

**Subagent delegation note:** this task is a strong candidate for hermetic subagent delegation per `model_selection_policy: voice-extraction routes to opus directly`. The subagent sees only the chapter files + OR-001, never the operator dialog. If the parent agent runs it in-line, document why in the completion report.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [AM-001#…], [SRC-…] for each sampled chapter
- **SCAN markers answered:** <count>
- **Chapters sampled:** <list of chapter_ids>
- **voice-anchor artifact:** VA-001
- **sample_excerpts count:** <N> spanning <M> chapters
- **tone_descriptors:** <list>
- **operator_overrides count:** <N>
- **Delegation:** subagent | in-line (with reason)
- **Discoveries:** <e.g., "Chapter 4 has a shift in voice that may be operator-edited round; flagged as F-NNN for operator review">
- **Recommended follow-up:** "T-003 ai-indicator-research can run next; T-005 unfinished-bits-scan can run in parallel."
