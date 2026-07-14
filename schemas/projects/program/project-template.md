# PROJECT.md — {{ project_name }}

> Orchestrator project for program-shaped work (`core/LOCK.md` §Programs). This
> project's subject matter is the program itself — a workstream registry, spawn /
> promote / retire decisions, and roll-up findings. It is a normal locked
> HyperWorker project in its own instance; it does not gain any coordination
> primitive the substrate doesn't already have. See `core/SUBSTRATE.md` §Single-Writer
> Rule.

## Status

active

## Lifecycle

{{ lifecycle }}

**Cadence:** {{ rollup_cadence }} (normalized to `cadence_days` at bootstrap; blank
if `lifecycle: terminal`). When `lifecycle: ongoing`, this project stays active
between roll-up cycles; it does not archive at the end of a cycle. See
`core/LOCK.md` §Ongoing Projects and `core/SUBSTRATE.md` §`hw cycle`.

## Program goal

{{ program_goal }}

## What this project owns

- The workstream registry (`WS-NNN` `workstream` artifacts) — one entry per sibling
  instance, status changes chained by supersede.
- Spawn, promote, and retire Decisions.
- Routing / priority Decisions between workstreams.
- Roll-up Findings, one per program cycle.

## What this project explicitly does NOT do

- **Execute workstream work.** The orchestrator plans, reviews, opens/closes loops —
  it never drafts a workstream's deliverable, never actuates a workstream's external
  surface, never completes a workstream's own tasks. See `00-REFERENCE-rules.md`
  Tier 1.
- **Write to a sibling instance's `events.jsonl`.** This project reads sibling
  projections (`SESSION-HANDOFF.md`, `CYCLES.md`) read-only. Any change to a
  sibling workstream is made by that workstream's own single writer, in its own
  session.
- **Bootstrap a sibling instance directly.** A spawn or promote Decision authorizes
  a new workstream; the actual `hw bootstrap` for that instance happens there, not
  here.
- **Nest a child project inside this instance.** Promotion is promote-and-swap — a
  new instance — never nesting. A parent and child are never simultaneously active
  in one instance.

## Workstream registry

Current registry: `projects/{{ project_id }}/workstreams/` (rendered from `WS-NNN`
artifacts, one file per current — non-superseded — entry). Full status history for
any workstream is the supersede chain, traversable from the current entry's
`reverses` field backward.

## Promote criteria

{{ promote_criteria }}

## Operator interruption budget

{{ interruption_budget }}

Anchored to `[OR-001#<short-hash>]`. `delegation_policy.pause_on` for this schema
always includes spawn-decision and promote-decision pause points, regardless of the
operator's declared list — see `artifact-extensions.yaml`.

## Phase shape

**Phase A — Setup.** Probe for existing sibling instances (T-000); register the
confirmed ones and stand up the registry projection (T-001).

**Phase B — Steady state (repeatable).** Spawn a new workstream when the operator
initiates one (T-002); promote a hot item out of an existing workstream into its own
dedicated one when it meets `promote_criteria` (T-003); retire a workstream once its
work is done or abandoned (T-005). Each is a branch of its task
(`hw branch T-00N <slug>` … `hw fold`), not a new task file per event.

**Phase C — Cycle (recurring, per `recurring_tasks:` in `schema.yaml`).** Roll up
every registered workstream's status read-only (T-004); close the cycle with
operator review, computing `next_due` (T-006).

## Scope

- workstream-inventory
- registry-standup
- workstream-spawn-protocol
- workstream-promote-protocol
- rollup-cycle
- workstream-retire-protocol
- program-review-and-cycle-close

## Hard scope boundaries

- No workstream-level deliverable content is produced in this project.
- No write access to any sibling instance's `events.jsonl`.
- Every spawn and every promote pauses for explicit operator approval before the
  workstream is registered — no exceptions, no "the operator's intent seemed clear."
- A workstream's status changes only via supersede (`reverses:` set); never an
  in-place registry edit.
- Cross-instance citations always carry a relative path and a content hash
  (`core/LOCK.md` §Programs point 4); a bare mention of a sibling workstream's state
  without a citation is not sufficient for a roll-up Finding or a promote Decision.

## Completion criteria

(Only relevant if `lifecycle: terminal`, or when the operator declares the
recurring need itself has ended on an ongoing program — see `core/LOCK.md`
§Ongoing Projects "Archive still exists.")

- Every registered workstream has a terminal status (`retired` or `done`); none
  remain `active` or `parked`.
- `hw verify` clean.
- Council pass at `project.archive`.
- Friction log reviewed for anything suggesting H-L3 needs revisiting (a
  coordination need this schema could not express in files — see README.md
  §Hypothesis under test).

## Started

{{ started_date }}

## Archived

(blank until done)
