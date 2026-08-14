# Open Loops — {{ project_id }}

> **Projection of the `loop.open` / `loop.close` events for one project.** Lives at `projects/<project-id>/OPEN-LOOPS.md`. Regenerated on every loop event; never hand-edited (`core/SUBSTRATE.md` §Projection rules).
>
> Why this file exists: a gated action once sat unconsumed for five weeks because "waiting on the operator's word" was a sentence in a message rather than a row in a table. This file records the rows; `hw status` reads them against today's date and leads with anything OVERDUE.

---

## Open

Newest first. Every column is a field the events recorded -- nothing here is computed from today's date.

| Loop | Waiting on | Opened | Stale after | Description |
|---|---|---|---|---|
| L-007 | external | YYYY-MM-DD | 7d | <one line: what is waiting, and what happens when it lands> |
| L-003 | operator-word | YYYY-MM-DD | 7d | <one line> |

**Liveness is not rendered here.** A loop is overdue once `Opened + Stale after` is in the past, which is a different answer every day for the same event prefix -- so computing it into this file would mean the same chain renders different bytes tomorrow, breaking the byte-determinism rule (`core/SUBSTRATE.md` §Projection rules, rule 2) and staling every citation to this projection overnight. `hw status` computes it at read time and leads with an **OVERDUE OPEN LOOPS** block, which is already its documented home (`core/SUBSTRATE.md` §`hw status`).

`Waiting on` is one of `operator-word`, `external`, `other-agent`, `scheduled`.

`(none)` when every loop is closed — which is the state to aim for.

## Closed

Oldest first; the record of what a loop turned into.

| Loop | Opened | Closed | Resolution |
|---|---|---|---|
| L-001 | YYYY-MM-DD | YYYY-MM-DD | <one line: what actually happened, including "no longer needed"> |

## Rendering protocol

A fresh agent must produce this file byte-identically from an event prefix alone (`core/SUBSTRATE.md` §Projection rules, rule 2). Pure replay: no clock is read at render time.

1. Filter `events.jsonl` to `loop.open` and `loop.close` events for this `project`, in append order.
2. A loop is open if its `loop.open` has no `loop.close` carrying the same `loop_id`. Open loops render in §Open ordered by `opened_at` descending (newest first); closed loops in §Closed ordered by `closed_at` ascending.
3. `Opened` is `opened_at`, date only. `Stale after` is `stale_after_days` as recorded, rendered `<n>d` (default `7` when the payload omits it). Both are copied, never computed.
4. `Description` and `Resolution` are the payload's fields, first line only, no line breaks.
5. Write the file, compute its SHA-256, and update `hashes.json` for `projects/<project-id>/OPEN-LOOPS.md`.

Re-render on every `loop.open` and `loop.close` -- and only then. `hw status` reads this file and computes overdueness against today; it never re-renders it, because nothing in it moves with the calendar.

## See also

- `core/SUBSTRATE.md` §Open Loops — payload schemas and the staleness rule; §`hw status` — the OVERDUE OPEN LOOPS block
- `core/VERIFICATION.md` §Layer 1 check 21 — `loop_close_without_open`, `duplicate_loop_open`, `handoff_missing_open_loops`
- `templates/session-handoff-template.md` — every handoff carries the open `L` ids
