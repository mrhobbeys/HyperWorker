# program schema

Run an orchestrator over N concurrent workstreams — each workstream its own harness
instance — as one normal locked HyperWorker project. Typically `lifecycle: ongoing`
(roll-up cycles on a cadence).

## What this is

A **program** is one operator goal decomposed into multiple concurrent workstreams:
many bid segments swept weekly with hot deals promoted to dedicated pursuit; one site
family with repair, SEO, and monetization in flight; one large rebuild staged across
eight subprojects (`core/LOCK.md` §Programs — read it first, it is the contract this
pack implements). The `program` schema is the orchestrator's own project schema. Its
subject matter *is* the program: a workstream registry (typed artifacts with a status
enum), spawn/promote/retire decisions, and roll-up findings. It is not a mechanism —
no orchestration primitive enters the substrate, the Lock is not loosened, and the
program instance never becomes a second writer on any workstream's `events.jsonl`
(`core/SUBSTRATE.md` §Single-Writer Rule).

## Hypothesis under test

This schema is **H-L3's test vehicle** (`core/LOCK.md` §Hypothesis table):

> Program-shaped work (many concurrent workstreams under one operator goal) is served
> by a *schema* — an orchestrator that is itself a locked project in its own instance —
> without any orchestration primitive entering the substrate.
>
> **Falsifier:** program operators need cross-instance atomicity, shared locks, or
> event routing that markdown-and-files cannot express, and are forced back to bespoke
> external coordination layers.

Every design choice below is answerable to that falsifier. If a task in this pack ever
needs to write into a sibling instance's `events.jsonl`, or needs a lock that spans two
instances, H-L3 is failing in the field and that is exactly the signal to report via
`friction.log`, not to work around quietly.

## Schema table

| Field | Value |
|---|---|
| **Schema** | `program` — an orchestrator that is itself a locked HyperWorker project; its artifacts are a workstream registry, spawn/promote/retire decisions, and roll-up findings over N sibling harness instances. |

## Artifacts

- **OR-001** — program goal, initial workstream inventory, roll-up cadence, promote
  criteria, operator interruption budget (`delegation_policy` passthrough).
- **WS-NNN** (`workstream`) — one registry entry per subproject workstream: id, name,
  relative instance path, schema it was bootstrapped from, lifecycle
  (`terminal`\|`ongoing`), status (`active`\|`parked`\|`promoted`\|`retired`\|`done`),
  last roll-up citation. Status changes are supersede events — the status history is a
  chain, never an in-place edit.
- **Decisions (DEC-NNN)** — spawn decisions, promote decisions, retire decisions,
  routing/priority calls. `synthesis_role` names which.
- **Findings (F-NNN)** — roll-up findings (one per cycle): workstream statuses,
  blockers, overdue cycles, promote/retire recommendations.
- **Anti-patterns (AP-NNN)** — recurring program-level dead ends (e.g., "a sweep
  workstream that never promotes anything after N cycles is a routing-rule problem,
  not a workstream problem").

## Tasks

T-000 workstream inventory (register existing instances; probe sweep) → T-001 registry
standup → T-002 spawn workstream (repeatable) → T-003 promote item (repeatable) → T-004
roll-up cycle (**recurring**) → T-005 retire workstream (repeatable) → T-006 program
review (**recurring** — cycle close + operator review).

T-002/T-003/T-005 are repeatable procedures, not one-shot tasks: each new spawn,
promote, or retire runs as a branch of the task (`hw branch T-002 <slug>` … `hw fold`,
per `core/ATOMICITY.md` §Branch/Fold), so the registry keeps growing without needing a
new task file per event. T-004/T-006 are the schema's `recurring_tasks:` — `hw cycle
close` resets them to `pending` for the next roll-up.

## The three rules that keep this a schema, not a mechanism

1. **One instance per workstream, always.** The program instance never appends to a
   workstream's `events.jsonl`. It reads projections (`SESSION-HANDOFF.md`,
   `CYCLES.md`) read-only and cites them by relative path + short hash.
2. **Promote-and-swap, not nesting.** A hot item inside a sweep workstream graduates
   to its own dedicated workstream (new instance, e.g. bootstrapped from
   `single-opportunity`). A parent and child are never simultaneously active in one
   instance.
3. **The orchestrator plans, reviews, opens/closes loops — it never does the work.**
   Program agents never execute workstream-level tasks. See
   `schemas/projects/program/rules-template.md` Tier 1.

## Notes

- No shell/browser needed by default. Agents get read access to sibling instance
  projections and write access only to the program instance
  (`capability-gates.yaml`).
- Evidence base: `reference/field-reports/2026-07-machine1-gather.md` §A (three
  independent field reinventions of this shape) and
  `reference/field-reports/laptop-hao-2026-07.md` "Rule-breaking / orchestrator usage"
  (a live production orchestrator brief, a hand-built agent-roster lane-boundary rule,
  a cross-project meta-tracker, and `course-master-plan-test`'s in-schema L1/L2/L3
  pattern — this schema generalizes the last one's slug-premise-pause and
  child-pause-skipped check to the program shape).
