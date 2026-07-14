# Bootstrap Probe — course-master-plan-test

> The probe runs at bootstrap, between `bootstrap_questions` answers and §Scope locking. It enumerates the L1 project's actual surface (the contents of `inputs/`) so operator can reconcile declared scope against ground truth. Per v5.1.1 §Bootstrap Inventory Sweep.

## Probe method

`filesystem-listing` — recursive walk of `<project root>/inputs/`.

## Declared source

`OR-001.platform_actuation.guide_path` is operator-declared (typically `<project root>/<platform>-site-guide.md`). At bootstrap the file does not exist yet (Phase A.2 produces it); declared `inputs/` corpus is the operator's stated set of resources to be present at A.1 execution.

For L1, `declared` at bootstrap is empty (the operator declares no specific filenames in `bootstrap_questions`). The probe surfaces the actual `inputs/` content as `found`; the diff is `missing_from_declared` only — operator confirms each item is in scope or marks excluded-after-discovery.

## Found source

Recursive walk of `<project root>/inputs/`. For each file:

1. Compute SHA-256 of file contents.
2. Record `{relative_path, size_bytes, sha256, mtime}`.
3. Files identified as obviously non-corpus (`.DS_Store`, `Thumbs.db`, `desktop.ini`) are excluded automatically; everything else is candidate corpus.

## Reconciliation flow

`per-item-disposition` — operator reviews the `bootstrap.inventory_diff` event payload (rendered to a temporary review file) and per-item:

- **confirm** — file is in scope as a corpus source for T-002 curriculum scan.
- **mark-excluded** — file is in `inputs/` but should not feed the corpus scan (e.g., a stray draft, an unrelated note); records as scope-item with terminal_state `excluded-after-discovery` at handoff.
- **defer** — file is corpus-relevant but not for THIS scan cycle (records as `deferred`).

After reconciliation, the executor emits `bootstrap.scope_locked` with the reconciled per-item list. PROJECT.md §Scope is written from the locked list.

## Skip path

If `inputs/` is empty (no files), the executor surfaces to operator: "Drop the main guiding resource dump into `inputs/` before continuing past Phase A.1. Reply `continue` when ready, or `continue without resources` to skip." If operator responds `continue without resources`, emit `bootstrap.probe_skipped` with `reason: "operator confirmed empty inputs/ — curriculum_discovery_mode will be set to from-draft pending operator-supplied draft master plan, or hybrid if a draft surfaces later."` and proceed.

## Layer 1 enforcement

Inherits substrate-level §Bootstrap Inventory Sweep behavior. The chain must contain either:

1. `bootstrap.inventory_diff` followed by `bootstrap.scope_locked` (operator_reconciliation populated), OR
2. `bootstrap.probe_skipped` with reason.

If neither is present at the first task.start of T-000 (or any task downstream), Layer 1 FAILs `bootstrap_probe_missing`.

## Hypothesis evaluation

Inherits substrate H-G3 (probe surfaces declared-vs-actual mismatches before §Scope locks). Falsifier: a wrong filename or missing-but-declared corpus file makes it past bootstrap and bites mid-T-002.
