# Bootstrap Probe — program

> Read by the executor at `hw bootstrap` time. The probe verifies the operator's
> declared `initial_workstream_inventory` against sibling instances that actually
> exist on disk, so the workstream registry reflects ground truth from the first
> registration, not an at-bootstrap guess. See `core/SUBSTRATE.md` §Bootstrap
> Inventory Sweep.

## Probe method

`sibling-instance-directory-sweep` — a filesystem walk, not a network probe. This is
the same shape as `course-master-plan-test`'s `filesystem-listing` probe, scoped to
harness instances instead of corpus files.

## Declared source

`OR-001.initial_workstream_inventory` items marked "existing" — each names a relative
instance path and a schema. Items marked "new" are NOT part of the probe's declared
set; they have no ground truth to check yet (`declared` for those stays empty and
`missing_from_found` never fires for them — they go through T-002's spawn-and-pause
protocol instead, per `core/LOCK.md` §Programs point 2: "the actual bootstrap happens
in the new instance, not this one").

## Found source

Recursive walk of the operator-declared search roots (typically the parent directory
of this program instance's own workspace — the field's three independent program
deployments all kept sibling instances as sibling directories). For each candidate
directory:

1. Check for `.hyperworker/events.jsonl`. Absence disqualifies the directory as a
   workstream candidate.
2. Read `projects/active_project.md` (or, if none active, the most recently archived
   or parked project under `projects/`) to determine `child_project_id`,
   `bootstrapped_from_schema` (from the project's `config.yaml` or PROJECT.md
   frontmatter), and current `lifecycle`.
3. Record `{relative_path, child_project_id, schema, lifecycle, active_project_status}`.

Directories with a `.hyperworker/` but no readable `active_project.md` and no
archived project either are recorded as `ambiguous` and left for operator
disposition rather than silently registered or silently dropped.

## Reconciliation flow

`per-item-disposition` — the operator reviews the `bootstrap.inventory_diff` event
payload (rendered to a temporary review file) and per item:

- **confirm** — the found instance is in scope; register it directly as a
  `workstream` artifact with `origin: existing-registered`.
- **exclude** — a found instance is not part of this program (a stray sibling
  directory, an unrelated project); records as excluded-after-discovery, no
  workstream artifact written.
- **declared-but-missing** — a declared "existing" item did not resolve to a real
  instance on disk (wrong path, not yet created). The operator either corrects the
  path and re-probes, or reclassifies it as "new" and routes it through T-002
  instead.

After reconciliation, the executor emits `bootstrap.scope_locked` with the confirmed
per-item list. PROJECT.md §Scope is written from that event; T-000 (workstream
inventory) consumes the locked list and registers each confirmed instance as a
`workstream` artifact.

## When to skip

If the operator declares no existing instances at all (`initial_workstream_inventory`
is entirely "new" items, i.e. the program starts from zero and every workstream will
be spawned through T-002), the probe emits `bootstrap.probe_skipped` with
`reason: "no existing instances declared — program starts from zero; all workstreams route through the T-002 spawn protocol"`
and T-000 proceeds directly to confirming that emptiness rather than walking a search
root that has nothing to find.

## Layer 1 enforcement

Inherits substrate-level §Bootstrap Inventory Sweep behavior. The chain must contain
either:

1. `bootstrap.inventory_diff` followed by `bootstrap.scope_locked`
   (`operator_reconciliation` populated), OR
2. `bootstrap.probe_skipped` with a reason.

If neither is present at the first `task.start` of T-000 (or any task downstream),
Layer 1 FAILs `bootstrap_probe_missing`.

## Cross-reference to T-000 and T-002

T-000 (workstream inventory) inherits the probe's confirmed instance list rather than
building one from scratch. T-000 registers each confirmed instance as a `workstream`
artifact with `origin: existing-registered` — these do NOT go through the
spawn-pause protocol (`capability-gates.yaml` §spawn_pause), because there is nothing
to pause on: the instance already exists and the operator is confirming it, not
approving its creation. Anything the operator declared "new" at bootstrap is
deliberately left unregistered here; it is picked up by T-002 the first time the
operator initiates that spawn.
