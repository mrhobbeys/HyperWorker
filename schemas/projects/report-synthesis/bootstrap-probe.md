# Bootstrap Probe — report-synthesis

> Read by the executor at `hw bootstrap` time. The probe enumerates the actual source corpus on disk, so §Scope reflects ground truth rather than the operator's recollection. See `core/SUBSTRATE.md` §Bootstrap Inventory Sweep.

## Default probe — filesystem listing

Synthesis projects declare an `input_folder` in their bootstrap answers. The probe walks that folder recursively and records every file the planner could plausibly treat as a source.

```
walk(input_folder, recursive=true)
filter(extension in [".md", ".pdf", ".txt", ".docx", ".html", ".rtf"])
```

Adjust the extension filter per project if the corpus declares a non-default form (transcripts as `.vtt`, code bundles as `.zip`, etc.). The probe records:

- `probe_method: "filesystem-listing"`
- `declared`: the list the operator named at bootstrap (often empty — operators frequently say "everything in input_folder" without enumerating). If the operator named specific files, those go in `declared`.
- `found`: the filtered file list.
- `missing_from_declared`: files on disk the operator did not name. The probe presents these so the operator can confirm "yes include all" or "exclude these specific items."
- `missing_from_found`: files the operator named but were not on disk. Candidates for filename correction or pre-bootstrap upload.

## Operator reconciliation

For corpora where the operator says "everything in input_folder," reconciliation is one keystroke: confirm the full found list. For curated subsets, the operator marks per-item include/exclude. For renamed or moved files, the operator points the probe at the correct path and re-runs.

After reconciliation, the agent emits `bootstrap.scope_locked` with the source-file list. PROJECT.md §Scope is written from that event; T-000 (source inventory) consumes the locked list.

## When to skip

If the corpus is large enough that filesystem walking is impractical (rare; most synthesis corpora fit in ten or fewer files but a few have hundreds), or if the corpus is partly external (URLs the agent must fetch), the probe emits `bootstrap.probe_skipped` with `reason: "<reason>"`. T-000 assumes responsibility for inventory in the skip case.

## Cross-reference to T-000

Synthesis schema's T-000 (source inventory) was previously the only place corpus-vs-declared reconciliation happened, and it ran after §Scope was already locked. The v5.1.1 probe runs before §Scope locks, so T-000 inherits a verified inventory rather than building one. T-000's deduplication step (SHA-256 hashing for byte-identical files) still runs against the locked list and adds finer-grained finding artifacts.
