---
id: T-000
kind: task
schema: report-synthesis
phase: A
risk_level: standard
required_tools: [file_read, file_write]
delivery_mode: constrained
depends_on: []
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "Every file in OR-001.input_folder is registered as a source artifact OR explicitly noted in the completion report as not-a-source (e.g., README, .gitignore) with the reason given."
  - "Each source has source_type, round, weight, and hash populated."
  - "Sources with detectable round relationships (e.g., 'audit.md' + 'audit-notes.md') have supersedes/superseded_by linked correctly."
  - "Source inventory projection regenerates byte-identical from events."
  - "Tier 4 STYLE in 00-REFERENCE-rules.md is populated (or explicitly marked 'no operator override beyond schema defaults' if the operator does not supply voice anchor or formatting overrides)."
  - "Banned tokens and canonical-facts tables in 00-REFERENCE-rules.md are either populated with operator-confirmed entries OR marked empty (table headers retained, body explicitly empty) — not left as placeholder rows."
---

# Task T-000: Source Inventory + Charter Anchor

## Objective

Catalog every input report in `OR-001.input_folder` as a `source` artifact. Establish round relationships between sources where filename conventions or content reveal them. Lock the operator-supplied voice/style/banned-tokens anchors in `00-REFERENCE-rules.md` so downstream extraction and drafting can reference them by tier.

This task absorbs the responsibilities the v5.0 schema split between T-000 (inventory) and T-001 (synthesis charter). v5.0.1 merges them: bootstrap already populates OR-001 (synthesis_purpose, target_audience, output_format, weighting_rule, excluded_topics, deliverable_path) and runs the project.activate council; a separate "charter" task after that has nothing to confirm. The remaining charter work — populating Tier 4 STYLE and the operator's banned tokens / canonical facts tables — folds in here.

## Step-by-Step Instructions

1. Read OR-001. Note `input_folder`, `weighting_rule`, `confidence_floor`, `synthesis_purpose`, `target_audience`, and `output_format`.
2. **Detect duplicates by hash.** Compute SHA-256 of each file in `input_folder` before registration. Two files with byte-identical content register as a single source artifact; flag the duplicate filename in the completion report.
3. List every file in `input_folder`.
4. For each file, determine `source_type` (audit, research, notes, draft, analysis, recommendation, etc.) by filename and a quick scan of the file's first 20 lines. Do not deeply read source contents at this step — claim extraction (T-002) is the content-read pass.
5. For each file, determine `round` (initial / notes / draft / correction / final / single). Filename conventions help: `-notes.md` suffix typically indicates a correction round; `-draft.md` indicates a draft. Ask the operator if ambiguous.
6. Detect supersedes relationships. If `01-website-audit.md` and `01-website-audit-notes.md` both exist, the notes round supersedes the initial round (operator may correct). Cite the older source's hash in the newer source's `supersedes:` field.
7. Set weight per source: default is `secondary`. Sources the operator names as primary in OR-001 (or that are obviously the latest corrected round of a key topic) get `primary`. Background context gets `contextual`.
8. For each file, run `hw add source < draft-src-NNN.md` per substrate protocol.
9. Update `superseded_by` on older sources after the newer source is registered (per SUBSTRATE.md §Superseded Artifact Back-Link).
10. **Charter anchor:** populate Tier 4 STYLE in `00-REFERENCE-rules.md`. If the operator declared a voice anchor or formatting override at bootstrap (or supplies one now), record it. If not, write the explicit line `No operator override beyond schema defaults; citation format per SUBSTRATE.md §Citation Format.`
11. **Banned tokens / canonical facts.** If the deliverable audience has banned tokens (regulated industry language, brand-voice carveouts) or canonical facts (specific dates, framework names, URLs that must appear verbatim), populate those tables in `00-REFERENCE-rules.md`. If neither applies, retain the table headers and add a single explicit "empty" row to make the operator's confirmation auditable rather than leaving the section ambiguous.
12. Answer @@SCAN markers from `00-REFERENCE-rules.md`.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…]
- **SCAN markers answered:** <count>
- **Outputs produced:** SRC-001 through SRC-NNN; updated 00-REFERENCE-rules.md (Tier 4 + banned-tokens + canonical-facts)
- **Files in input_folder not registered as sources:** <list with reason — e.g., "README.md describes folder structure">
- **Duplicate-by-hash sources detected:** <list of duplicate filenames + the canonical SRC-NNN they collapsed to>
- **Voice/style decision:** <"operator override: <verbatim>" or "no override beyond schema defaults">
- **Discoveries:** <e.g., "Filename convention X applies; flagged as F-001 for downstream tasks">
- **Recommended follow-up:** "Operator review source weights before claim extraction begins."
