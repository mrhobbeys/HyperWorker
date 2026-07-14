# Bootstrap Probe — content-piece-test

> Read by the executor at `hw bootstrap` time. Per operator directive DEC-001 (forthcoming at scaffold), the per-piece inputs folder is a **post-kickoff artifact** — it is created empty at scaffold-time, the operator populates it after scaffolding completes, and the actual probe runs deferred when the operator says "check the folder."

## Scaffold-time behavior (this run)

At scaffold-time, the executor:

1. Creates `projects/<piece-slug>/inputs/` (empty).
2. Emits `bootstrap.probe_skipped` with `reason: "inputs/ folder is post-kickoff artifact per operator directive DEC-001; operator will populate then signal check; T-000 source-inventory inherits responsibility for actual file enumeration."`
3. Tells operator: "Scaffolding complete. Drop your raw material into `projects/<piece-slug>/inputs/`. When ready, tell me to check the folder, and I will run T-000."

This satisfies the v5.1.1 substrate Layer 1 `bootstrap_probe` check (which accepts either `bootstrap.inventory_diff` + `bootstrap.scope_locked` OR `bootstrap.probe_skipped` with reason).

## Post-population probe (deferred)

When operator says check, the executor:

1. Walks `projects/<piece-slug>/inputs/` recursively. Filters `.md`, `.txt`, `.pdf`, `.docx`, `.html`, `.rtf`, `.vtt` (voice-memo transcripts), `.srt`.
2. Emits `bootstrap.inventory_diff` with `{declared: [], found: <files>, missing_from_declared: <files>, missing_from_found: [], operator_reconciliation: null}`.
3. Surfaces the file list to the operator. Operator confirms "include all" or marks per-item exclude.
4. Emits `bootstrap.scope_locked` with the reconciled list. PROJECT.md §Scope is updated from this event's payload.
5. T-000 (source-inventory) runs against the locked list. SHA-256 dedup at T-000 step 2 catches byte-identical duplicates.

## Operator override

If the operator hits "check the folder" before populating, the deferred probe finds zero files. The agent surfaces the empty result and asks whether to defer further or to refuse-and-stop (thinness-watcher pattern at the bootstrap level — content-piece work cannot proceed with zero source material AND zero interview turns; the lens alone is not enough material).
