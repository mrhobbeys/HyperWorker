# Cycles — {{ project_id }}

> **Projection of the `cycle.open` / `cycle.close` events for one `lifecycle: ongoing` project.** Lives at `projects/<project-id>/CYCLES.md`. Regenerated from `events.jsonl` on every cycle event; never hand-edited (`core/SUBSTRATE.md` §Projection rules). The events are the source of truth — in particular `next_due` is computed at close and recorded **on the `cycle.close` event**, so "when is the next sweep due" is substrate state rather than prose in a handoff.
>
> Terminal-lifecycle projects have no CYCLES.md. A `cycle.open` or `cycle.close` on a project whose `PROJECT.md` does not declare `lifecycle: ongoing` is a Layer 1 FAIL (`cycle_on_terminal_lifecycle`; see `core/VERIFICATION.md` §Layer 1 check 17).

---

## Cadence

- **Declared:** {{ cadence }} — recorded verbatim from `[OR-001#<short-hash>]` (e.g. `weekly`, `P7D`, a cron expression)
- **Normalized:** `cadence_days: {{ cadence_days }}` — computed once at bootstrap so due-date math never re-parses prose
- **Next due:** {{ next_due }} — from the most recent `cycle.close`; `(open cycle)` while a cycle is in flight, `(none yet)` before the first close

## Cycles

One row per cycle, oldest first. `Closed` and `Next due` are blank for the open cycle; there is at most one.

| Cycle | Opened | Closed | Next due | Summary |
|---|---|---|---|---|
| C-001 | YYYY-MM-DD | YYYY-MM-DD | YYYY-MM-DD | <one-line summary from the cycle.close payload> |
| C-002 | YYYY-MM-DD | YYYY-MM-DD | YYYY-MM-DD | <...> |
| C-003 | YYYY-MM-DD | — | — | (open) |

## Status

<One of:>

- **Open:** `C-NNN` opened `YYYY-MM-DD`. Recurring tasks for this cycle: see `hw next-step`.
- **Idle:** last cycle `C-NNN` closed `YYYY-MM-DD`; next due `YYYY-MM-DD`.

**Overdue is not rendered here.** Whether `Next due` has passed is a different answer every day for the same event prefix, so computing it into this file would mean the same chain renders different bytes tomorrow -- breaking the byte-determinism rule (`core/SUBSTRATE.md` §Projection rules, rule 2) and staling every citation to this projection overnight. `hw status` compares `Next due` against today at read time and leads with the OVERDUE line, which is already its documented home (`core/SUBSTRATE.md` §`hw status`, `core/LOCK.md` §Ongoing Projects) — the weekly sweep stops depending on anyone remembering it is Tuesday.

---

## Rendering protocol

A fresh agent must be able to produce this file byte-identically from an event prefix (`core/SUBSTRATE.md` §Projection rules, rule 2). Pure replay: no clock is read at render time.

1. Filter `events.jsonl` to `cycle.open` and `cycle.close` events for this `project`, in append order.
2. Walk them pairwise. Each `cycle.open` starts a row keyed by its `cycle_id`; the `cycle.close` carrying the same `cycle_id` fills that row's `Closed` (`closed_at`, date only), `Next due` (`next_due`), and `Summary` (`summary`, first line, no line breaks). An unmatched trailing `cycle.open` renders as the open row with `—` in both date columns and `(open)` as the summary.
3. `Cadence` comes from the most recent `cycle.open` payload (`cadence`, `cadence_days`); before the first cycle both read from `OR-001`.
4. `Next due` in §Cadence is the `next_due` of the last `cycle.close`; `(open cycle)` if a later `cycle.open` has no matching close, `(none yet)` if no cycle has closed.
5. §Status renders **Open** when a `cycle.open` has no matching close, and **Idle** otherwise, carrying the last close's `closed_at` and `next_due` verbatim. It never compares a date against today; `hw status` does that at read time.
6. Write the file, compute its SHA-256, and update `hashes.json` for `projects/<project-id>/CYCLES.md`.

Re-render on every `cycle.open` and `cycle.close`. `active_project.md` is re-rendered in the same step: the pointer stays on the project (an ongoing project does not archive at cycle close) and only its `Next due:` line changes.

## See also

- `core/SUBSTRATE.md` §Lifecycle events, §`hw cycle close` / `hw cycle open`, §Projections
- `core/LOCK.md` §Ongoing Projects
- `core/VERIFICATION.md` §Layer 1 check 17 — `cycle_close_without_open`, `cycle_open_without_close`, `cycle_on_terminal_lifecycle`, `wrap_with_open_cycle`
- `templates/session-handoff-template.md` — the other per-project projection an agent reads when resuming cold
