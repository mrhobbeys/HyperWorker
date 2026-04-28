# Bootstrap Probe — software-feature-ship

> Read by the executor at `hw bootstrap` time. The probe enumerates source files in scope so §Scope reflects ground truth. See `core/SUBSTRATE.md` §Bootstrap Inventory Sweep.

## Default probe — git ls-files

For software-feature-ship projects in a git repository, the canonical probe is:

```
git ls-files <declared-scope-paths>
```

Where `<declared-scope-paths>` are the paths the operator declared at bootstrap (e.g., `src/auth/`, `migrations/`, `apps/api/routers/users.py`). The probe collects every file path matching at least one declared path.

The probe records:

- `probe_method: "git-ls-files"`
- `declared`: the path list the operator provided.
- `found`: the actual file list under each declared path.
- `missing_from_declared`: files in `found` that don't appear in `declared` (e.g., the operator named a directory; the probe surfaces individual files).
- `missing_from_found`: declared paths that don't exist (typo, renamed, moved).

## Operator reconciliation

For directory-declared scope, the diff almost always shows individual files in `missing_from_declared` — that's normal and the operator confirms "all files under this directory." For renamed-file mismatches in `missing_from_found`, the operator either provides the new path or removes the entry.

After reconciliation, the agent emits `bootstrap.scope_locked`. PROJECT.md §Scope captures both the directory-level and file-level scope.

## Non-git projects

Pre-git projects or non-versioned codebases use `probe_method: "filesystem-listing"` against the declared paths. The diff shape is identical; the source enumeration is just `os.walk` instead of `git ls-files`. Operators on Mercurial or Pijul use the equivalent `hg files` / `pijul ls` and record the relevant `probe_method`.

## When to skip

Brand-new feature work in a fresh module (no files yet) skips the probe with `reason: "no existing files in scope; module created during this session"`. The skip should be rare — most software-feature-ship work touches existing code.
