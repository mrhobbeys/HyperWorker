---
id: T-000
kind: task
schema: course-master-plan-test
phase: A
phase_step: 1
risk_level: standard
required_tools: [file_read, file_write, hash_compute]
delivery_mode: constrained
depends_on: []
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "Every file in <project root>/inputs/ is registered as a source artifact OR explicitly noted in the completion report as not-a-source (README, .gitignore, system files) with reason."
  - "Each source has source_type, round, weight, and SHA-256 hash populated."
  - "Source inventory projection regenerates byte-identical from events."
  - "bootstrap.inventory_diff event has been emitted with declared/found/missing fields populated."
  - "Operator reconciliation captured in operator_reconciliation; bootstrap.scope_locked emitted with the locked per-item list (or bootstrap.probe_skipped emitted if inputs/ was empty + operator confirmed skip)."
  - "PROJECT.md §Scope is rewritten from bootstrap.scope_locked payload — not the bootstrap_questions provisional values."
  - "OR-001.curriculum_discovery_mode is supersed if T-000's content scan reveals a different mode than the bootstrap default (e.g., draft master plan present → from-draft or hybrid)."
  - "Tier 4 STYLE in 00-REFERENCE-rules.md is populated, or marked 'no override beyond schema defaults' explicitly."
---

# Task T-000: Bootstrap Inventory Sweep on `inputs/`

## Objective

Catalog every file in `<project root>/inputs/` as a `source` artifact. Run the v5.1.1 `bootstrap.inventory_sweep` ceremony so PROJECT.md §Scope is locked against ground truth, not against operator's at-bootstrap declared list.

This task absorbs report-synthesis T-000's source-inventory pattern (SHA-256 dedup + register-once) plus the v5.1.1 bootstrap-probe ceremony. The downstream T-002 curriculum corpus scan reads only what T-000 registered.

## Step-by-Step Instructions

1. Read OR-001. Note `course_name`, `lens_anchor`, `cross_project_scope`, `platform_actuation.guide_path`. Confirm `inputs/` location: `<project root>/inputs/` (alongside `HyperWorker-5.0/`, NOT inside it). If operator overrode this in OR-001, follow the override.

2. **Read `schemas/projects/course-master-plan-test/bootstrap-probe.md`.** Execute the filesystem-listing probe.

3. **Detect duplicates by hash.** Compute SHA-256 of each file in `inputs/` before registration. Two byte-identical files register as a single source artifact; flag the duplicate filename in the completion report.

4. List every file in `inputs/`. Exclude `.DS_Store`, `Thumbs.db`, `desktop.ini` automatically.

5. For each file, determine `source_type` (research, notes, draft, analysis, recommendation, audit, calendar, blueprint, roadmap, interview, competitive-brief, other) by filename and a quick scan of the first 20 lines. Do not deeply read source contents — content reads happen at T-002.

6. For each file, determine `round` (initial / notes / draft / correction / final / single). Filename conventions help.

7. Detect supersedes relationships. If two filenames suggest one corrects the other (e.g., `course-strategy.md` + `course-strategy-notes.md`), cite the older source's hash in the newer source's `supersedes:` field.

8. Set weight per source: default `secondary`. Sources the operator names as primary at bootstrap (or that are obviously the latest corrected round of a key topic) get `primary`. Background context gets `contextual`.

9. For each registered source, run `hw add source < draft-src-NNN.md` per substrate protocol.

10. **Emit `bootstrap.inventory_diff`** with `{schema, probe_method: filesystem-listing, declared: [], found: <list>, missing_from_declared: <list>, missing_from_found: [], operator_reconciliation: null}`.

11. **Reconcile with operator.** Surface the diff: per file, operator confirms / marks-excluded / defers. Capture per-item dispositions in a follow-up event populating `operator_reconciliation`.

12. **Emit `bootstrap.scope_locked`** with the reconciled per-item list. Or, if `inputs/` was empty + operator confirmed `continue without resources`, emit `bootstrap.probe_skipped` with reason and proceed.

13. **Update OR-001 if needed.** If T-000's section-summary scan reveals a different `curriculum_discovery_mode` than the bootstrap default (`from-corpus`), supersede OR-001 with the corrected mode.

14. **Charter anchor:** populate Tier 4 STYLE in `00-REFERENCE-rules.md`. If operator declared no voice override beyond `OR-001.lens_anchor`, write the explicit line `No override beyond schema defaults; voice anchored to OR-001.lens_anchor[0]; citation format per SUBSTRATE.md §Citation Format.`

15. Answer @@SCAN markers from `00-REFERENCE-rules.md`.

## Completion Report (filled by executor)

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…]
- **SCAN markers answered:** <count>
- **Outputs produced:** SRC-001 through SRC-NNN; bootstrap.inventory_diff EV-NNNN; bootstrap.scope_locked EV-NNNN (or bootstrap.probe_skipped); updated 00-REFERENCE-rules.md Tier 4
- **Files in inputs/ not registered as sources:** <list with reason>
- **Duplicate-by-hash sources detected:** <list>
- **Supersedes chains detected:** <list>
- **curriculum_discovery_mode:** <from-corpus | from-draft | hybrid> (with reason if changed from bootstrap default)
- **Discoveries:** <findings observed during inventory; e.g., "corpus is heavily research-shaped, not a draft master plan; T-002 should expect to surface candidate structures, not validate a pre-existing one">
- **Recommended follow-up:** "Operator review source weights before T-002 corpus scan begins."
