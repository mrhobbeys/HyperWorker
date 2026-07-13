# Bootstrap Probe — cleanroom-rebuild

> Read by the executor at `hw bootstrap` time. The probe enumerates the original application's observable surface, so §Scope reflects ground truth rather than the operator's recollection. See `core/SUBSTRATE.md` §Bootstrap Inventory Sweep. The probe runs in the OBSERVATION room: everything it touches faces the original, and everything it records is an observed-zone fact. The walled build executor must never consume the probe's raw output.

## Default probe — observation-surface sweep

Cleanroom projects declare a `legacy_system`, an `observation_oracle`, and a `build_executor` in their bootstrap answers. The probe verifies that each declared surface is actually reachable before §Scope locks:

- **Original launchable/drivable.** Launch (or confirm running) the original application and drive one trivial interaction via the declared observation oracle. If the original cannot be started or driven, nothing downstream can be measured.
- **Observation tooling reachable.** Exercise each channel the oracle declares — GUI driver responds to a probe command, SQL trace attaches, direct DB access answers a catalog query. A declared-but-dead channel is recorded in the diff, not discovered at T-003.
- **Declared screens/modules exist.** For each screen or module the operator named at bootstrap, confirm it is reachable in the running original (menu entry, navigation path, or window title). Screens the original exposes that the operator did not name are surfaced for reconciliation.
- **Build executor exists and is walled.** Confirm the declared `build_executor` (local model endpoint) answers a health check, AND verify it structurally LACKS access to the original: no network route to the original's host, no filesystem mount of its binaries or database, no tool in its capability set that could reach either. A build executor that can see the original is a wall breach at minute one.

The probe records:

- `probe_method: "observation-surface-sweep"`
- `declared`: the surface items the operator named at bootstrap — screens/modules, DB objects, peripherals, observation channels, and the build executor endpoint.
- `found`: the surface items the probe actually reached — screens enumerated in the running original, catalog objects the DB answered for, channels that responded, the executor health-check result plus its isolation verdict.
- `missing_from_declared`: surface the probe found that the operator did not name (extra screens, undeclared tables, an attached peripheral). Presented so the operator can pull them into scope or mark them out-of-scope explicitly.
- `missing_from_found`: items the operator named that the probe could not reach (a renamed screen, a dropped table, a dead trace channel, an unreachable executor). Candidates for correction, tooling repair, or removal from scope before observation begins.

## Operator reconciliation

The operator disposes of each diff item: confirm a found-but-undeclared screen into scope (or exclude it with a reason recorded against `OR-001.excluded_scope`), correct a misnamed module, repair or replace a dead observation channel, or fix the build executor's isolation before proceeding — an executor that fails the isolation check blocks `bootstrap.scope_locked`; it is not a reconcilable diff item.

After reconciliation, the agent emits `bootstrap.scope_locked` with the verified surface list. PROJECT.md §Scope is written from that event; T-000 (target inventory) consumes the locked list.

**Wall note.** The probe's raw captures (screenshots, trace output, catalog dumps) are `source=original` facts. If persisted, they are written to `observed/` only, and are never consumable by build agents. The build executor's own health check is the single probe step that runs outside the observation surface — it must be performed without passing any original-derived content to the executor.

## When to skip

If the original cannot be run at bootstrap time (hardware not yet assembled, environment still being restored) or the observation tooling is not yet installed, the probe emits `bootstrap.probe_skipped` with `reason: "<reason>"`. T-000 then assumes responsibility for the full surface enumeration, and the wall charter task (T-001) must still verify build-executor isolation before any Phase D task can start. Skipping the probe never waives the isolation check — it only defers it.

## Cross-reference to T-000

T-000 (target inventory) was previously the only place declared-vs-actual reconciliation happened, and it ran after §Scope was locked. The probe runs before §Scope locks, so T-000 inherits a verified surface list rather than building one from scratch. T-000 still does the deep enumeration — one OBS artifact per screen, per DB object, per peripheral, with `capture_method` and `source_ref` populated — against the locked list; the probe only establishes that the surface is reachable and matches what the operator declared.
