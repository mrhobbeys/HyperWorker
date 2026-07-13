---
id: T-000
kind: task
schema: content-piece-test
phase: A
risk_level: standard
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: []
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "Every file in `projects/<piece-slug>/inputs/` is registered as a source artifact OR explicitly noted in the completion report as not-a-source (README, .gitignore) with reason."
  - "Each source has source_type, round, weight, hash populated."
  - "Sources with detectable round relationships (e.g., draft + correction) are linked via supersedes/superseded_by."
  - "Source inventory projection regenerates byte-identical from events."
  - "Tier 4 STYLE in 00-REFERENCE-rules.md is populated (or marked 'no operator override beyond schema defaults; voice_anchor is canonical')."
---

# Task T-000: Source Inventory

## Objective

Catalog every input in `projects/<piece-slug>/inputs/` as a `source` artifact. The folder was populated post-scaffolding by the operator (per DEC-001).

This task assumes the inputs folder is non-empty. If it is empty, the agent surfaces that to the operator and asks whether to defer (operator will add material) or to refuse-and-stop (thinness protocol — content-piece work cannot proceed with zero sources and the operator should reconsider whether this piece has enough material).

## Step-by-Step Instructions

1. Read OR-001. Note `piece_slug`, `voice_anchor`, `default_lens`, `central_angle_supplied`, `formats[]`.
2. List every file in `projects/<piece-slug>/inputs/` recursively.
3. **Detect duplicates by hash.** Compute SHA-256 of each file. Two files with byte-identical content register as a single source artifact; flag the duplicate filename in the completion report.
4. For each file, determine `source_type`:
   - `tweet` — single tweet text (typically a `.txt` or short `.md`).
   - `x-article` — X long-form article draft.
   - `voice-memo-transcript` — typically `.txt`, `.vtt`, `.srt` from a voice memo or video.
   - `notes` — operator's freeform notes file.
   - `originating-post` — earlier published version of the same idea (e.g., the originating tweet for an expanded piece).
   - `draft` — operator's prior rough draft on this topic.
5. For each file, determine `round` (single | draft | correction | final). Most piece-1 inputs are `single` (one expression of the idea); rounds apply when operator supplies multiple revisions.
6. Set `weight` per source: default `secondary`. `primary` for the source the operator names as the originating piece (e.g., "expand the X article" → that article is primary). `contextual` for background notes.
7. For each file, run `hw add source < draft-src-NNN.md` per substrate protocol (frontmatter from artifact-templates/source-template.md).
8. Update `superseded_by` on older sources after newer sources are registered.
9. **Tier 4 STYLE anchor:** confirm that 00-REFERENCE-rules.md Tier 4 reads "voice_anchor is canonical; see OR-001.voice_anchor verbatim" and not stale placeholder content.
10. Answer @@SCAN markers from 00-REFERENCE-rules.md (Tier 1, Tier 2, Tier 3, Tier 4).

## Completion Report

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…]
- **SCAN markers answered:** <count>
- **Outputs produced:** SRC-001 through SRC-NNN
- **Files in inputs/ not registered as sources:** <list with reason>
- **Duplicate-by-hash sources detected:** <list of duplicates + canonical SRC-NNN>
- **Discoveries:** <e.g., "Originating tweet is short — X article is the primary expansion source.">
- **Recommended follow-up:** "Proceed to T-001 corpus scan."
