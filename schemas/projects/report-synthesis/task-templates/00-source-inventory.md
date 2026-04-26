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
  - "Every file in OR-001.input_folder is registered as a source artifact OR explicitly noted in completion report as not-a-source (e.g., README, .gitignore)."
  - "Each source has source_type, round, weight, and hash populated."
  - "Sources with detectable round relationships (e.g., 'audit.md' + 'audit-notes.md') have supersedes/superseded_by linked correctly."
  - "Source inventory projection is regenerable from events."
---

# Task T-000: Source Inventory

## Objective

Catalog every input report in `OR-001.input_folder` as a `source` artifact. Establish round relationships between sources where filename conventions or content reveal them (e.g., `01-website-audit.md` + `01-website-audit-notes.md`).

## Step-by-Step Instructions

1. Read OR-001. Note `input_folder`, `weighting_rule`, and `confidence_floor`.
2. List every file in `input_folder`.
3. For each file, determine source_type (audit, research, notes, draft, analysis, recommendation, etc.) by filename and a quick scan of the file's first 20 lines. Do not deeply read source contents at this step.
4. For each file, determine round (initial / notes / draft / correction / final / single). Filename conventions help: `-notes.md` suffix typically indicates a correction round; `-draft.md` indicates a draft. Ask the operator if ambiguous.
5. Detect supersedes relationships. If `01-website-audit.md` and `01-website-audit-notes.md` both exist, the notes round supersedes the initial round (operator may correct). Cite the older source's hash.
6. Set weight per source: default is `secondary`. Sources the operator names as primary in OR-001 (or that are obviously the latest corrected round of a key topic) get `primary`. Background context gets `contextual`.
7. For each file, run `hw add source < draft-src-NNN.md` per substrate protocol.
8. Update `superseded_by` on older sources after the newer source is registered.
9. Answer @@SCAN markers from 00-REFERENCE-rules.md.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…]
- **SCAN markers answered:** <count>
- **Outputs produced:** SRC-001 through SRC-NNN
- **Files in input_folder not registered as sources:** <list with reason — e.g., "README.md describes folder structure">
- **Discoveries:** <e.g., "Filename convention X applies; flagged as F-001 for downstream tasks">
- **Recommended follow-up:** "Operator review source weights before claim extraction begins."
