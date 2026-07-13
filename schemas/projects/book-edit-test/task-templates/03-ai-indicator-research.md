---
id: T-003
kind: task
schema: book-edit-test
phase: A
risk_level: standard
required_tools: [file_read, file_write, web_fetch, web_browse]
delivery_mode: bounded-iteration
delivery_mode_fields:
  preview_surface: "schemas/projects/book-edit-test/working/ai-indicator-research/"
  version_naming: "ai-indicator-candidates-v{pass}.md"
  convergence_criterion: "operator approves a final banned-pattern subset OR three passes elapsed"
  max_passes: 3
depends_on: [T-000]
consumes:
  - "[OR-001#<short-hash>]"
  - "[VA-001#<short-hash>] (voice anchor — to ensure the candidate list does not flag the author's actual voice as 'AI-generated')"
acceptance_criteria:
  - "Subagent produced a candidate list of current (≤6 months old as of project run) AI-indicator patterns from credible sources (style guides, editor blog posts, publisher guidelines, peer-reviewed analyses, well-cited LinkedIn/Substack pieces). At least 5 sources cited."
  - "Each candidate has: pattern, pattern_kind (literal | regex | unicode-codepoint), pattern_class, replacement_rule (if applicable), source citation (URL or document reference)."
  - "Each candidate is cross-checked against VA-001: if the candidate would flag the author's actual voice as 'AI', the candidate is annotated 'CONFLICTS WITH VOICE ANCHOR' and the operator must decide explicitly to add it (otherwise it's auto-rejected)."
  - "Operator reviewed every candidate and marked: approve / reject / defer."
  - "Approved candidates are registered as banned-pattern artifacts with source: ai-indicator-research and source_citation: [DEC-NNN#hash] of the operator-approval Decision."
  - "An ai-indicator-policy Decision (DEC-NNN, synthesis_role: ai-indicator-policy) is appended capturing the operator's full approve/reject/defer answers verbatim."
---

# Task T-003: AI-Indicator Research

## Objective

Use a hermetic web-research subagent to surface the current list of "this looks AI-written" patterns (from style guides, editor blogs, publisher guidelines, peer-reviewed analyses), cross-check each candidate against the voice-anchor (so we don't flag the author's actual voice), and present the survivors to the operator for approve/reject/defer per item. Approved items become banned-pattern artifacts that every chapter pass `consumes:`.

This is the only task in the project with web access. The subagent is delegated with `web_fetch` + `web_browse` capabilities; the parent agent does not have these.

## Step-by-Step Instructions

1. Read OR-001 and VA-001 voice-anchor.
2. **Delegate to a hermetic subagent** with capability declaration `[file_read, file_write, web_fetch, web_browse]`. The subagent's prompt:
   - Research the current (April 2026 ±6 months) list of patterns that have come to be flagged as "AI-generated writing" by editors, style guides, publisher guidelines, and analytical writing.
   - Sources to consult: editor industry blogs, traditional publisher submission guidelines, prominent Substack analyses on AI-prose detection, academic linguistics papers on LLM-output stylometry, well-cited LinkedIn/Twitter threads from senior editors. Aim for at least 5 distinct credible sources.
   - For each pattern, capture: the pattern itself (exact phrase or regex), the pattern_kind, the pattern_class (per the banned-pattern artifact schema enum), a one-sentence rationale, the source citation.
   - Cross-check each pattern against VA-001 sample_excerpts. If a candidate would flag the author's actual voice (e.g., the candidate is "begins sentence with 'Importantly,'" and VA-001 shows the author does use "Importantly," at sentence start), annotate the candidate `CONFLICTS WITH VOICE ANCHOR — operator must decide explicitly`.
   - Output a candidate list at `working/ai-indicator-research/ai-indicator-candidates-v1.md` with one section per candidate.
3. **Surface the candidate list to the operator.** Brief format:
   - Total candidates surfaced: N
   - Candidates flagged as conflicting with voice anchor: M
   - Candidates with no voice conflict: N - M
   - One-line summary of the highest-frequency / most-cited patterns
   - Pointer to the working file for full details
4. **Operator marks each candidate** approve / reject / defer.
   - Approve: the operator agrees this pattern should not appear in the polished manuscript.
   - Reject: the operator wants to keep this pattern (or it conflicts with voice and operator chose to keep voice).
   - Defer: the operator wants to think about it; revisit at Phase D final-read.
5. **For approved candidates:** register each as a banned-pattern artifact. `source: ai-indicator-research`, `source_citation: [DEC-NNN#hash]` (the policy Decision from step 6), `confidence: validated`. Run `hw add banned-pattern < draft.md` per artifact.
6. **Append the ai-indicator-policy Decision.** `synthesis_role: ai-indicator-policy`. Body: every candidate listed verbatim with the operator's verdict (approve | reject | defer) and the reason if the operator gave one. The Decision is the source of truth for what was considered and what was decided; the banned-pattern artifacts are derived projections of the approved subset.
7. **Update 00-REFERENCE-rules.md Banned patterns table** with all newly-approved BP-NNN entries.
8. **Bounded-iteration revisit:** if the operator rejects all or most candidates because the research surfaced patterns that conflict with the voice anchor, the subagent may be re-spawned (max 3 passes total) with a refined prompt to focus on patterns less voice-coupled. Document the revisit in the completion report.
9. Answer @@SCAN markers.

## Specific guidance

**Voice-anchor cross-check is non-negotiable.** A subagent that surfaces a candidate list without annotating voice conflicts produces work the operator cannot trust — the operator would need to manually compare each candidate against VA-001, defeating the point of the research. Layer 2 verification rejects an output that lacks the cross-check column.

**Source diversity matters.** A candidate list that draws from one Substack post is weak signal. Five+ distinct sources, with at least one traditional publisher / academic source, is the bar.

**Defer is a real answer.** Some patterns are situationally bad — fine in technical writing, signal-of-AI in narrative. Operator may defer until they see the pattern in context during chapter passes; the deferred candidates remain in the policy Decision but don't become banned-pattern artifacts (yet).

**The deferred set is consulted at final-read.** T-012 final-read consumes the ai-indicator-policy Decision and surfaces deferred candidates if they appear in the assembled manuscript.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…], [VA-001#…]
- **SCAN markers answered:** <count>
- **Subagent passes:** <1-3>
- **Candidates surfaced (final pass):** <N>
- **Voice-conflict candidates:** <M>
- **Operator verdicts:** approved=<X>, rejected=<Y>, deferred=<Z>
- **banned-pattern artifacts registered:** BP-NNN through BP-MMM
- **ai-indicator-policy Decision:** DEC-NNN
- **Sources cited:** <count, with one-line summary of the top 3>
- **Discoveries:** <e.g., "The 'rule of three' pattern surfaces frequently but conflicts with VA-001's first-person-plural-list-of-three signature; operator deferred">
- **Recommended follow-up:** "T-005 unfinished-bits-scan can run next (T-004 may run in parallel)."
