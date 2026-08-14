# Mechanism: Lock — Single Project Focus

> Drift across multiple "active" projects is the dominant attention-leak in operator practice. Two projects "in progress" means neither gets the operator's full reading of state at any given moment; decisions made in one project bleed into the other; context never warms enough to catch the drift before it ships. A single project lock with backlog intake eliminates the leak without losing capture.

---

## Hypothesis

| ID | Claim | Falsifier |
|---|---|---|
| H-L1 | A single project lock with deliberate switch-protocol prevents the operator-facing failure where multiple projects drift simultaneously. | Operator runs two projects concurrently in one harness instance and reports cleaner outcomes than running them sequentially. |
| H-L2 | A first-class ongoing lifecycle (cycles with a computed `next_due`) removes the field-improvised workarounds — `deferred (ongoing)` terminal states, cadence-in-prose, perpetual projects that can never truthfully archive. | Operators on `lifecycle: ongoing` projects still invent orchestrator-side status conventions, or overdue cycles silently accumulate because the OVERDUE flag is ignored as ceremony. |
| H-L3 | Program-shaped work (many concurrent workstreams under one operator goal) is served by a *schema* — an orchestrator that is itself a locked project in its own instance — without any orchestration primitive entering the substrate. | Program operators need cross-instance atomicity, shared locks, or event routing that markdown-and-files cannot express, and are forced back to bespoke external coordination layers. |

**Field status of H-L1 (2026-07).** Not falsified. Two deployments that attempted concurrent writers inside one instance corrupted the substrate (see `core/SUBSTRATE.md` §Single-Writer Rule); every deployment retreated to one-instance-per-workstream. What the field *did* demonstrate, three independent times, is an unnamed coordination layer built above instances — which is what §Programs names. Evidence: `reference/field-reports/`.

---

## Substrate

Lock state lives in three event kinds: `project.activate`, `project.archive`, `project.park`, plus `backlog.add` / `backlog.remove`. The active project is whichever was last activated and not archived or parked. Projections:

- `projects/active_project.md` — pointer to the currently active project, or "(none)".
- `backlog.md` — flat list of unactivated entries with priority and tags.

Both projections regenerate from events on every Lock-affecting write.

---

## Active-Project Projection

```markdown
# Active Project

**Current:** <project-name>
**ID:** <project-id>
**Path:** projects/<project-id>/PROJECT.md
**Schema:** <schema-name>
**Activated:** <YYYY-MM-DD>
**Status:** in_progress

## Quick Context
<one-sentence summary derived from PROJECT.md objective>
```

If no project is active:

```markdown
# Active Project

**Current:** (none)

The harness has no active project. Use `hw bootstrap --schema <name> --name <id>` to start one, or `hw log <text>` to capture an idea without activating.
```

---

## Backlog Projection

`backlog.md` is rendered from all `backlog.add` events not subsequently removed, grouped by priority then tag:

```markdown
# Backlog

## HIGH

- **<entry_id>** — <text>  
  *tags: <tag1>, <tag2>* · *added <YYYY-MM-DD>*

## MEDIUM

- ...

## LOW

- ...
```

The backlog is flat by design. No nested project structure. No priority inheritance. No auto-aging. Operators promote entries to projects via `hw bootstrap`; entries that never get promoted stay until manually removed.

---

## The Switch Protocol

Switching projects is two events, never one:

1. `project.archive` (or `project.park`) on the current project.
2. `project.activate` on the new project.

When the operator says "switch to project X," emit both. If `project.activate` arrives without a prior archive/park, the harness refuses: "<old-project> is still active. Run `hw park` or `hw wrap` first."

This is a structural check, not a verbal request. The agent cannot accidentally activate two projects, because the projection regeneration protocol refuses to write `active_project.md` pointing at two paths.

**Enforced as of v6.0.0.** The paragraph above was true only of the projection; the event log accepted the second `project.activate` without complaint, and a field deployment appended exactly that — no park, no archive, no refusal, because the refusal lived in this file rather than in the verifier. `hw verify` now FAILs `lock_activate_without_release` on any `project.activate` for a different project while one is still active (`core/VERIFICATION.md` §Layer 1 check 15). Bootstrap (the first activate) and re-activating the project already holding the Lock (`hw bootstrap --resume`) are legal; `_harness`-scoped meta events never move the Lock.

---

## Distraction Intake

The operator drops an idea unrelated to the active project. The failure mode is "just outline it real quick" — the agent starts drafting, the parent project's context gets polluted by tangent work, and 20 minutes evaporate before anyone notices the operator never agreed to switch. Capture the idea as a backlog event and stay on the active project. Nothing else.

The protocol for `hw log <text>`:

1. Acknowledge the idea in one sentence.
2. Synthesize a backlog entry: short title + one-paragraph body + suggested priority + tags inferred from text.
3. Append `backlog.add` event. Render `backlog.md`. Confirm: *"Logged as `<entry_id>` (priority: `<X>`). Continuing on `<active-project>`."*
4. Do not draft, sketch, or "just outline." The intake is event-write only.

If the operator pushes for execution: *"To work on this now I'll need to park `<active-project>`. Park it, or stay on it?"* Do not infer the answer.

You will know you have followed this protocol when the active project's TASK-STATE.yaml is unchanged after a distraction-intake exchange.

---

## Project Completion (`hw wrap`)

When the active project's tasks are all `complete` and Layer 2 verification passes:

1. **Discovery sweep.** Read recent events for the project: any `verify.layer2.fail` retries, any rejected `task.recite` paraphrases, any `branch.fold` results that surfaced surprises. Invite the operator to write findings (`hw add finding`) before archiving.
2. **Append `project.archive`.** Payload includes a one-paragraph summary drafted from PROJECT.md plus a count of artifacts emitted.
3. **Re-render `active_project.md`** to "(none)".
4. **Present top-3 backlog.** Read `backlog.md`, take the three highest-priority entries, present them. The operator picks one (or none).
5. **If selected, run `hw bootstrap`** with the schema the operator declares for the chosen entry.

The archived project's projections remain in `projects/<id>/`. They are not deleted — they are off the critical path.

---

## Park Protocol (`hw park`)

`hw park` demotes the active project to the backlog without archiving (the project is not done; the operator wants to step away).

1. Append `project.park` with reason.
2. Append `backlog.add` re-listing the project at its current state.
3. Re-render `active_project.md` and `backlog.md`.

A parked project resumes via `hw bootstrap --resume <project-id>` (re-activates without scaffolding).

---

## Ongoing Projects (`lifecycle: ongoing`) — v5.3

Some real work has no terminal state: a weekly opportunity sweep, a shared-service registry, a standing maintenance plan. Before v5.3 these either could never truthfully archive, or improvised a `deferred (ongoing)` status and handed their fate to an off-harness convention — two deployments independently invented exactly that. The lifecycle is now declared, not improvised.

- **Declaration.** The schema (or `PROJECT.md` at bootstrap) declares `lifecycle: ongoing` and a `cadence` (recorded verbatim, normalized once to `cadence_days`). Default remains `lifecycle: terminal`; nothing changes for existing schemas.
- **Cycles instead of completion.** Work proceeds in cycles: `cycle.open` → the schema's `recurring_tasks:` run to `complete` → `hw cycle close` records a summary and a computed `next_due` **on the event**. The project stays active (or parks); it does not archive. Protocols in `core/SUBSTRATE.md` §`hw cycle`.
- **Overdue is structural.** `hw status` on an ongoing project leads with `OVERDUE` when `next_due` has passed with no new cycle opened. The weekly sweep stops depending on anyone remembering it's Tuesday.
- **The Lock is unchanged.** An ongoing project occupies the instance's single active slot like any other; it parks and resumes the same way. What changes is only that "done for now, back next week" is a first-class state with a date the substrate can check.
- **Archive still exists.** When the recurring need itself ends, the operator says so and `hw wrap` runs normally. An ongoing project with an open cycle cannot wrap (Layer 1).

---

## Programs — v5.3

A **program** is one operator goal decomposed into multiple concurrent workstreams: many bid segments swept weekly with hot deals promoted to dedicated pursuit; one site family with repair, SEO, and monetization in flight; one large rebuild staged across eight subprojects. The field built this three separate times, each with the same shape, each without a name for it. This section names it. **It is a pattern plus a schema, not a mechanism** — no orchestration primitive enters the substrate, and the Lock is not loosened.

The shape:

1. **One instance per workstream.** Every subproject runs in its own harness instance — own `events.jsonl`, own lock, own single writer (`core/SUBSTRATE.md` §Single-Writer Rule). Concurrency lives *between* instances, never inside one.
2. **The orchestrator is itself a locked project.** The program gets its own instance, bootstrapped from the `program` schema (`schemas/projects/program/`). Its subject matter *is* the program: a subproject registry (typed artifacts with status enums), routing and priority decisions, roll-up findings, promote/retire events for workstreams. The deployment that ran its orchestrator this way accumulated fourteen clean, citable decisions; the deployments that ran orchestration as loose convention accumulated postmortems.
3. **Promote-and-swap, not nesting.** When a candidate inside a sweep project gets hot, the orchestrator records a promote decision and a dedicated project is bootstrapped in a new instance (e.g., from `single-opportunity`). A parent and child are never simultaneously active in one instance.
4. **Cross-instance references are paths plus hashes.** A program artifact cites a subproject artifact by relative path and content hash — the same staleness signal as any citation, computable without any shared runtime.
5. **Roll-up is a cycle task.** The program project is typically itself `lifecycle: ongoing`: each program cycle reads subproject `SESSION-HANDOFF.md` / `CYCLES.md` projections (read-only — never another instance's `events.jsonl` as a writer) and records a roll-up finding.

What this deliberately is not: a shared lock, a cross-instance event bus, a scheduler, or a harness-of-harnesses runtime. If program-scale coordination outgrows files — leases, serialized concurrent writes, dashboards — that is tooling, and tooling ships as a sibling project in the Hyper ecosystem, not as substrate.

---

## Why a Single File for the Pointer

`active_project.md` is one line of meaningful content. Splitting it across files (`status.md`, `current.md`, etc.) creates ambiguity about which file wins. One file, regenerated from one event kind, is structurally simpler.

Multi-project parallelism runs across instances, not inside one: if two workstreams must run simultaneously, each gets its own harness instance with its own `events.jsonl`. The Lock is per-instance, not global. When the parallel workstreams serve one goal and need coordination, that coordination is itself a project — see §Programs.

---

## Relationship to Other Mechanisms

| Mechanism | Interaction |
|---|---|
| Atomicity | Decomposes the locked project into tasks. |
| Typed Artifacts | All artifacts are scoped to the active project; cross-project visibility is opt-in (see `core/TYPED-ARTIFACTS.md` §Cross-Project). |
| Verification | Council runs at `project.activate` (Verification Checkpoint) and at `project.archive` boundaries. |
| Precedence | The active project's `00-REFERENCE-rules.md` is the rule set in force. |
