# Mechanism: Lock — Single Project Focus

> Drift across multiple "active" projects is the dominant attention-leak in operator practice. A single project lock with backlog intake eliminates the leak without losing capture.

---

## Hypothesis

| ID | Claim | Falsifier |
|---|---|---|
| H-L1 | A single project lock with deliberate switch-protocol prevents the operator-facing failure where multiple projects drift simultaneously. | Operator runs two projects concurrently in one harness instance and reports cleaner outcomes than running them sequentially. |

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

The backlog is flat by design. There is no nested project structure, no priority inheritance, no auto-aging. Operators promote entries to projects via `hw bootstrap`; entries that never get promoted stay until manually removed.

---

## The Switch Protocol

Switching projects is two events, never one:

1. `project.archive` (or `project.park`) on the current project.
2. `project.activate` on the new project.

If the operator says "switch to project X," the agent emits both. If `project.activate` arrives without a prior archive/park, the harness refuses: "<old-project> is still active. Run `hw park` or `hw wrap` first."

This is a structural check: the agent cannot accidentally activate two projects, because the projection regeneration protocol will refuse to write `active_project.md` pointing at two paths.

---

## Distraction Intake

When the operator drops an idea unrelated to the active project, the agent runs `hw log <text>`. The protocol:

1. Acknowledge the idea in one sentence.
2. Synthesize a backlog entry: short title + one-paragraph body + suggested priority + tags inferred from text.
3. Append `backlog.add` event. Render `backlog.md`. Confirm to the operator: *"Logged as `<entry_id>` (priority: `<X>`). Continuing on `<active-project>`."*
4. Do not draft, sketch, or "just outline." The intake is event-write only.

If the operator pushes for execution: *"To work on this now I'll need to park `<active-project>`. Park it, or stay on it?"* The agent does not infer the answer.

---

## Project Completion (`hw wrap`)

When the active project's tasks are all `complete` and Layer 2 verification passes:

1. **Discovery sweep.** Read recent events for the project: any `verify.layer2.fail` retries, any rejected `task.recite` paraphrases, any `branch.fold` results that surfaced surprises. The operator is invited to write findings (`hw add finding`) before archiving.
2. **Append `project.archive`.** Payload includes a one-paragraph summary the agent drafts from PROJECT.md plus a count of artifacts emitted.
3. **Re-render `active_project.md`** to "(none)".
4. **Present top-3 backlog.** Read `backlog.md`, take the three highest-priority entries, present them to the operator. The operator picks one (or none).
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

## Why a Single File for the Pointer

`active_project.md` is one line of meaningful content. Splitting it across files (`status.md`, `current.md`, etc.) creates ambiguity about which file wins. One file, regenerated from one event kind, is structurally simpler.

Multi-project parallelism is a process problem, not a harness problem. If two unrelated workstreams must run simultaneously, run two harness instances with separate `events.jsonl`. The Lock is per-instance, not global.

---

## Relationship to Other Mechanisms

| Mechanism | Interaction |
|---|---|
| Atomicity | Decomposes the locked project into tasks. |
| Typed Artifacts | All artifacts are scoped to the active project; cross-project visibility is opt-in (see `core/TYPED-ARTIFACTS.md` §Cross-Project). |
| Verification | Council runs at `project.activate` (Verification Checkpoint) and at `project.archive` boundaries. |
| Precedence | The active project's `00-REFERENCE-rules.md` is the rule set in force. |
