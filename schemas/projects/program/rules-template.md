# 00-REFERENCE-rules — {{ project_name }} (program)

Precedence tiers resolve rule conflicts (see `precedence-tiers.yaml`). Highest tier
(lowest ordinal) wins. Same-tier conflicts are an authoring error and block tasks.

## Tier 1 — ABSOLUTE (never overridden)

- **One `events.jsonl` has at most one writer, always.** This instance never appends
  to a sibling workstream's `events.jsonl` — not to record a status change, not to
  fix an obvious typo, not because it would be faster than waiting for that
  instance's own session. See `core/SUBSTRATE.md` §Single-Writer Rule.
- **A parent and a child are never simultaneously active in one instance.**
  Promotion is promote-and-swap — a hot item gets a NEW dedicated instance — never
  nesting. See `core/LOCK.md` §Programs point 3.
- **The orchestrator plans, reviews, opens/closes loops — it never does the work.**
  A program agent never drafts a workstream's deliverable, never executes a
  workstream's own tasks, never actuates a workstream's external surface. If
  routing implies work, the work is opened as a loop in the workstream's own
  instance (a Decision here, a task there), never performed in this instance. This
  generalizes the field's hand-built agent-roster lane-boundary rule ("a task
  needing a change outside its lane OPENS A LOOP, never does it directly") from a
  bespoke workaround to a schema rule.
- **Operator decisions are FINAL:** record verbatim, never re-open or contradict.
  Raise a concern once, then comply.
- **The actual bootstrap of a new or promoted workstream happens in the new
  instance, not this one.** This project authorizes; it does not scaffold.

## Tier 2 — REGISTRY-SCOPE

- This project owns the workstream registry, routing/priority decisions, and
  roll-up findings. Nothing else.
- Every spawn and every promote STOPS after the proposal (`workstream.spawn_proposed`)
  and waits for explicit operator approval (`workstream.spawn_decided`,
  `operator_confirmed: true`) before the workstream is registered. There is no
  "skip the pause because the operator's intent seemed clear" path in this schema.
- A roll-up cycle reads `SESSION-HANDOFF.md` / `CYCLES.md` **read-only**. It never
  opens a sibling instance's `events.jsonl` as a writer (Tier 1).
- Promote citations go **both ways**: this project's promote Decision cites the
  source item by relative path + hash (`source_item_citation`); the source
  workstream's own item is marked `promoted` and cites this Decision back — by
  that workstream's own writer, in its own session, not by this instance reaching
  into the source.

## Tier 3 — DECISION-DISCIPLINE

- Spawn, promote, retire, and routing calls are typed Decision artifacts
  (`synthesis_role`: `spawn-decision` | `promote-decision` | `retire-decision` |
  `routing-decision`), never loose conversation.
- A workstream's status changes only via a new `workstream.add` event with
  `reverses:` set to the current `WS-NNN` — never an in-place registry edit. The
  status history is a supersede chain (`core/SUBSTRATE.md` §Superseded Artifact
  Back-Link).
- Every cross-instance reference cites both a relative path and a content hash
  (§Cross-Instance Citation Format below), so staleness is checkable without a
  shared runtime.

## Tier 4 — STYLE

- Same-instance citations: `[KIND-NNN#hash]` per `core/SUBSTRATE.md` §Citation
  Format.
- Cross-instance citations: see §Cross-Instance Citation Format below.
- Workstream names in the registry match the sibling instance's own PROJECT.md
  title.

---

## Cross-Instance Citation Format

A program artifact cites a sibling workstream's projection by **relative path plus
the first 12 lowercase hex characters of the SHA-256 of the cited file's bytes at
citation time** — the same staleness signal as any citation, computable without any
shared runtime (`core/LOCK.md` §Programs point 4):

```
<relative-instance-path>/projects/<child-project-id>/SESSION-HANDOFF.md@sha256:a3f9c2b1e0f4
```

**Staleness check.** At any later read, recompute the SHA-256 of the file at that
path and compare the first 12 hex characters to the cited value:

| Result | Meaning |
|---|---|
| Path resolves, hash matches | Fresh — nothing has changed at the source since citation. |
| Path resolves, hash differs | Stale — expected and informational. The sibling instance moved on since the citation was written; this is normal, not corruption. Re-cite if the roll-up needs current state. |
| Path does not resolve | Broken — the sibling instance's projection moved or the `instance_path` is wrong. Surface to operator; do not silently drop the workstream from the registry. |

This is distinct from same-instance citation freshness (`hashes.json` /
`[KIND-NNN#hash]`), which is enforced at Layer 1 for every event in *this*
instance's own chain. Cross-instance citations are checked by the roll-up and
promote tasks themselves, per `capability-gates.yaml` §rollup_citation.

## @@SCAN markers

- @@SCAN_1_1: Did any event in this turn append to, or attempt to append to, a
  sibling instance's `events.jsonl`?
- @@SCAN_1_2: Did this turn execute or draft workstream-level deliverable work
  (rather than plan, review, or open/close a loop about it)?
- @@SCAN_2_1: If this turn registered a spawned workstream, did the sibling
  instance's existence get confirmed by the operator BEFORE registration, rather
  than assumed?
- @@SCAN_3_1: Did this turn change a workstream's status by anything other than a
  new `workstream.add` with `reverses:` set?
- @@SCAN_3_2: Does every spawn/promote/retire/routing decision in this output cite
  the workstream(s) it concerns by `[WS-NNN#hash]`?
