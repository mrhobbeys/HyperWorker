# Open Loops — {{ project_id }}

> **Projection of the `loop.open` / `loop.close` events for one project.** Lives at `projects/<project-id>/OPEN-LOOPS.md`. Regenerated on every loop event; never hand-edited (`core/SUBSTRATE.md` §Projection rules).
>
> Why this file exists: a gated action once sat unconsumed for five weeks because "waiting on the operator's word" was a sentence in a message rather than a row in a table. `hw status` leads with anything here marked OVERDUE.

---

## Open

Newest first. `Age` is days since `opened_at`; a loop is **OVERDUE** once `Age` exceeds `Stale after`.

| Loop | Waiting on | Opened | Age | Stale after | Description |
|---|---|---|---|---|---|
| L-007 | external | YYYY-MM-DD | 3d | 7d | <one line: what is waiting, and what happens when it lands> |
| L-003 | operator-word | YYYY-MM-DD | **37d — OVERDUE** | 7d | <one line> |

`Waiting on` is one of `operator-word`, `external`, `other-agent`, `scheduled`.

`(none)` when every loop is closed — which is the state to aim for.

## Closed

Oldest first; the record of what a loop turned into.

| Loop | Opened | Closed | Resolution |
|---|---|---|---|
| L-001 | YYYY-MM-DD | YYYY-MM-DD | <one line: what actually happened, including "no longer needed"> |

## Rendering protocol

A fresh agent must produce this file byte-identically from an event prefix plus a date (`core/SUBSTRATE.md` §Projection rules, rule 2). `Age` and the OVERDUE marker are the one date-dependent part; everything else is pure replay.

1. Filter `events.jsonl` to `loop.open` and `loop.close` events for this `project`, in append order.
2. A loop is open if its `loop.open` has no `loop.close` carrying the same `loop_id`. Open loops render in §Open ordered by `opened_at` descending (newest first); closed loops in §Closed ordered by `closed_at` ascending.
3. `Age` is whole days from `opened_at` to today, rendered `<n>d`. When `Age` exceeds `stale_after_days` (default `7` when the payload omits it), render it bold with ` — OVERDUE` appended.
4. `Description` and `Resolution` are the payload's fields, first line only, no line breaks.
5. Write the file, compute its SHA-256, and update `hashes.json` for `projects/<project-id>/OPEN-LOOPS.md`.

Re-render on every `loop.open` and `loop.close`, and on any `hw status` that recomputes staleness (the age column moves with the calendar even when no event lands).

## See also

- `core/SUBSTRATE.md` §Open Loops — payload schemas and the staleness rule; §`hw status` — the OVERDUE OPEN LOOPS block
- `core/VERIFICATION.md` §Layer 1 check 21 — `loop_close_without_open`, `duplicate_loop_open`, `handoff_missing_open_loops`
- `templates/session-handoff-template.md` — every handoff carries the open `L` ids
