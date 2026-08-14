# Bootstrap Probe — book-edit-test

> Read by the executor at `hw bootstrap` time. The probe enumerates the actual corpus on disk, so §Scope reflects ground truth rather than the operator's recollection. See `core/SUBSTRATE.md` §Bootstrap Inventory Sweep.

## Default probe — filesystem listing

book-edit projects declare a `source_manuscript_path` (canonical), `input_folder` (per-chapter working files), `archive_folders` (older rounds), and optionally `candidates_folder` (notes / unincorporated content) at bootstrap. The probe walks each declared folder and records what it finds.

```
walk(source_manuscript_path)               # one file
walk(input_folder, recursive=true)
walk(archive_folders[*], recursive=true)
walk(candidates_folder, recursive=true)    # if declared
filter(extension in [".docx", ".doc", ".md", ".txt", ".rtf", ".pdf", ".html"])
```

The probe records:

- `probe_method: "filesystem-listing"`
- `declared`: list of paths the operator named at bootstrap (typically just the four folders + canonical manuscript). Per-file enumeration is normally not declared; the operator says "everything in these folders."
- `found`: the filtered file list from the walk, with each file tagged by which folder it came from.
- `missing_from_declared`: files on disk in a declared folder. The probe presents these so the operator can confirm "yes include all" or mark per-item exclusions.
- `missing_from_found`: declared paths that don't exist. Candidates for filename correction or pre-bootstrap upload.
- `chapter_count_estimate`: heuristic count of chapters in the source manuscript by reading paragraph styles / heading levels (informational; not authoritative).

## Per-folder operator reconciliation

For each folder, the operator confirms which files are in scope:

- **source_manuscript_path:** confirm this is the file Phase A's chapter-split task should consume. Typically a single docx.
- **input_folder:** typically empty at bootstrap (Phase A T-001 populates it). Probe surfaces any pre-existing files for the operator to confirm — they may be hand-prepared per-chapter splits, in which case T-001's behavior changes (preserve those, don't overwrite).
- **archive_folders:** confirm files to register as `chapter-source` artifacts with role `archive-original` or `archive-edited`. These are hash-pinned and never edited.
- **candidates_folder:** confirm files the operator wants the candidates-evaluation task (T-004) to consider for fold-in.

## Round inference

When archive folders contain naming conventions like `Chapter N Draft V1.docx` and `Chapter N Draft V2.docx` (or similarly versioned filenames), the probe infers a round chain (V1 → V2). The chain inference is presented to the operator for confirmation; the probe does not silently lock the chain. If the operator's manuscript history is not naming-convention-driven (e.g., timestamped backups, branch-named files), the operator names the chain explicitly.

## Chapter-count estimate

The probe opens the canonical manuscript file (read-only) and counts heading-level paragraphs (Heading 1 styles, "Chapter N" prose patterns, manual page break + bold-large-text sequences). The estimate is reported in the inventory_diff as a heuristic — the canonical chapter count is established by T-001 (chapter-split), which produces the assembly-map artifact.

The estimate exists so the operator can sanity-check: if the probe estimates 14 chapters and the operator knows there are 10, the source manuscript may have a structural issue (extra dividers, mid-chapter breaks miscounted, etc.) worth investigating before T-001 runs.

## Operator reconciliation output

After per-folder confirmation, the executor emits `bootstrap.scope_locked` with a structured scope-item list:

- One scope item per chapter (estimated count, finalized at T-001).
- One scope item per chapter-edit-pass task (mirrors chapters; populated when T-001 produces the assembly-map).
- One scope item per non-chapter-pass task (T-000 through T-006, T-008 through T-013).
- One scope item for each deliverable in OR-001: deliverable_path, voice_guidelines_path, print_ready_path (if print_ready_required).

§Scope is then written into PROJECT.md from this event.

## When to skip

If the corpus is partly external (URLs, cloud storage the agent must fetch) or if filesystem walking is not possible in the operator's environment, the probe emits `bootstrap.probe_skipped` with `reason: "<reason>"`. T-000 then assumes responsibility for inventory in the skip case.

## Cross-reference to T-000

T-000 (corpus-inventory) consumes the locked scope and registers each file as a `chapter-source` artifact. T-000 also runs the SHA-256 deduplication pass for byte-identical files (rare but possible across the round chain). The probe runs before §Scope locks; T-000 inherits a verified inventory rather than building one.
