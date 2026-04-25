# Mechanism: Atomicity — One Task, Hermetic Working Set, Capability-Gated

> An atomic task fits in one session, with a declared upstream working set and a declared tool capability requirement. Branch/fold preserves exploratory subwork in events while keeping the parent context clean. Capability gates prevent the v4.1.1 failure mode where subagents were delegated work without the tools to do it.

This mechanism subsumes v4.1.1's Dependency mechanism. Dependencies are now declared per task in `consumes:` (artifact citations) and `depends_on:` (task IDs); the dependency graph is a projection (`TASK-STATE.yaml`) over `task.create`, `task.status`, and `task.complete` events.

---

## Hypotheses

| ID | Claim | Falsifier |
|---|---|---|
| H-A1 | A task that fits one session, has a hermetic working set, and declares its tool requirements eliminates drift caused by oversize work or missing tools. | Drift observed in a task that passed all three predicates. |
| H-A2 | Branch/fold preserves the sub-trajectory in events while keeping the parent context clean. | Parent context grew unboundedly during a branch. |
| H-A3 | Schema-level capability gates prevent the v4.1.1 subagent tool-mismatch failure. | Subagent attempted a tool call for a tool it was not granted. |

---

## Task Structure

```
projects/<id>/tasks/<task-id>/
  task.md              # canonical instructions (Mutable Surface)
  consumed-inputs.md   # projection (recitation; regenerated each consumption)
  branches/            # subtask branches (created on hw branch)
    <branch>/
      task.md
      result.md        # projection of branch.fold
done/
  <task-id>/           # moved here on task.complete
    task.md
    completion-report.md
    post-mortem.md     # optional, narrative, file-canonical
```

`task.md` is the operator/planner-authored instruction file. It is not event-sourced; it is part of the Mutable Surface. Status transitions (`task.create`, `task.status`, etc.) are event-sourced and projected into `TASK-STATE.yaml`.

---

## Task Frontmatter

```yaml
---
id: T-007
kind: task
schema: marketing-campaign      # links to project schema for capability/verification config
phase: 2
risk_level: standard            # standard | elevated | critical (locked at authoring)
required_tools: [file_write, web_browse]
delivery_mode: prescribed       # prescribed | constrained | bounded-iteration
depends_on: [T-005, T-006]
consumes:
  - "[OR-001#a3f9c2b1e0f4]"     # operating-reality
  - "[DEC-002#b8d4e1779a02]"    # decision
  - "[F-014#c1d2e3f4a5b6]"      # finding
  - "[AP-005#d2e3f4a5b6c7]"     # anti-pattern
acceptance_criteria:
  - "Subject line ≤ 50 characters."
  - "Word count between 150 and 300."
  - "Reading level Flesch-Kincaid ≤ 8."
  - "Zero Tier 1 violations from 00-REFERENCE-rules.md."
---
```

| Field | Purpose |
|---|---|
| `id` | `T-NNN`, unique within project. |
| `schema` | Project schema; determines defaults for capability gates and verification config. |
| `phase` | Phase grouping. Phase boundaries may be checkpoints (see Verification). |
| `risk_level` | Determines verification layers required (see `core/VERIFICATION.md`). Locked at task creation; not changed mid-execution. |
| `required_tools` | Tool capabilities the task needs. The harness composes a subagent's tool schema by intersection with `agents/<agent>.yaml` `provides:`. |
| `delivery_mode` | One of three (see below). |
| `depends_on` | Task IDs that must be `complete` before this task is `pending → in_progress`. |
| `consumes` | Typed-artifact citations the task reads as upstream working set. Hermetic: nothing else is mounted. |
| `acceptance_criteria` | Layer 2 verification targets. Each must be observable and pass/fail. |

---

## Hermetic Working Set

The agent executing this task reads, in addition to `task.md`:

1. `00-REFERENCE-rules.md` for the active project (Tier 1 rules cannot be hidden by hermeticism).
2. The project's compressed reference content (`*.compressed.md`; see `core/TYPED-ARTIFACTS.md` §Compression).
3. Each artifact in `consumes:` — read-only, by exact ID and hash.
4. `templates/executor-prompt.md`.

Anything outside that list is **not** mounted. If the agent needs another artifact, it must `STOP` and emit a `task.status` to `blocked` with a `reason: missing_consumes <artifact>`. The planner adds the artifact to `consumes:` and unblocks.

This is the v5.0 form of "Do NOT Touch": positive scope by enumeration of `consumes:`, not negative scope by enumeration of forbidden files.

---

## Delivery Modes

| Mode | Who writes | When |
|---|---|---|
| `prescribed` | Planner authors content during planning; executor pastes it exactly. | Regulated, brand-critical, or legally sensitive content. |
| `constrained` | Executor generates content within declared boundaries. | Most creative or technical work. |
| `bounded-iteration` | Executor produces N candidates against a preview surface; operator selects or redirects; capped by max passes. | Visual / design / copy exploration where first-pass fidelity is impossible. |

`bounded-iteration` requires three additional fields:

```yaml
preview_surface: "https://staging.example.com/banner-preview"
version_naming: "banner-v{N}.png"
convergence_criterion: "operator approves OR three passes elapsed"
max_passes: 3
```

The agent STOPs on convergence or max-passes, whichever comes first. Iteration is bounded.

---

## Task State Projection (`TASK-STATE.yaml`)

`TASK-STATE.yaml` is a projection. The render protocol:

1. Group `task.create` events by `phase`. For each phase, list tasks in ID order.
2. For each task, compute current status as the most recent `task.status` event's `to` value (or `pending` if no status events). If the latest event is `task.complete`, status is `complete`.
3. Write `consumes` and `depends_on` from frontmatter (which the `task.create` payload captured).

```yaml
project: "<project-id>"
last_event: "EV-0123"
phases:
  1:
    name: "Foundation"
    checkpoint: null
    tasks:
      - id: T-001
        title: "..."
        status: complete
        risk_level: standard
        depends_on: []
        consumes: ["[OR-001#a3f9...]"]
        completed_at: "2026-04-26T11:14:09Z"
  2:
    name: "Nurture"
    checkpoint: "PAUSE — operator approves Phase 1 outputs"
    tasks:
      - id: T-002
        ...
```

The projection is byte-deterministic from events: same event prefix → same YAML. Operators who hand-edit `TASK-STATE.yaml` will lose their edits on next regeneration.

---

## State Machine

```
pending → in_progress → complete
   │           │           │
   ├──────────►│           │
   │           ▼           │
   └──── blocked ◄─────────┘
              │
              ▼
            failed
```

Legal transitions (the agent emits `hw write <task-id> --status <state>` to record):

| From | To | Trigger |
|---|---|---|
| `pending` | `in_progress` | Agent starts the task; all `depends_on` must be `complete`. |
| `in_progress` | `blocked` | Pushback, missing consumes, conflict, ambiguity. |
| `in_progress` | `complete` | Layer 2 verification passes. |
| `blocked` | `pending` | Planner resolved the block. |
| `complete` | `blocked` | Ratchet failure — a later task invalidated this one's output (see Ratchet). |
| `in_progress` | `failed` | Repeated Layer 1 / Layer 2 failures past retry budget. |

`hw write` rejects illegal transitions. The substrate enforces the state machine; the agent does not "decide" whether to advance.

---

## Branch / Fold

When a task needs exploratory subwork — drafting alternatives, investigating an unknown — the agent emits `hw branch <task-id> <branch-name>`. See `core/SUBSTRATE.md` §`hw branch` for the protocol.

**Inside a branch.** The branch is a fresh atomic task. Its `task.md` declares its own `consumes` (often a subset of the parent's), its own `acceptance_criteria`. Its events are tagged with the branch ID and aggregated under `branch.event` envelopes.

**Folding.** `hw fold <task-id>/<branch> --result "<text>"` collapses the branch:

1. The branch's full event sub-trajectory remains in `events.jsonl` under `branch.event` payloads.
2. A 1–3 sentence `result.md` projection is written to `branches/<branch>/result.md`.
3. The parent's read-set on next turn includes only `result.md`, not the branch trajectory.

**Why this is structural.** The parent's context window does not have the choice of "remember the whole branch." The branch trajectory is in the log, but the projection the parent reads is the result. Context discipline is enforced by the projection rendering protocol, not by the agent's restraint.

---

## Capability Gates

Each subagent profile declares what tools it provides:

```yaml
# .hyperworker/agents/web-research.yaml
agent_id: web-research
provides: [file_read, web_browse, web_fetch]
description: "Subagent for browser-mediated research tasks."
```

A task declares what tools it requires:

```yaml
required_tools: [file_write, web_browse]
```

**Delegation gate.** When the parent agent intends to delegate this task to a subagent, the harness composes the subagent's tool schema as `agent.provides ∩ task.required_tools`.

- If `task.required_tools ⊆ agent.provides`, the subagent receives exactly the required tools. Delegate.
- Otherwise, the harness **refuses to delegate** and emits `capability.gap` with `{task_id, agent_id, missing_tools}`. It writes `projects/<id>/tasks/<task-id>/capability_gap.md` listing the missing tools and the available alternatives.

**Fallback paths.** When a gap is reported, the operator chooses:

1. Run in-line on the parent agent (which has full tools).
2. Add the missing capability to an existing agent profile.
3. Spawn a different agent with the required tools.

The agent never silently degrades or attempts a tool not in its schema. The schema *is* the boundary; "did the agent comply" is not a question.

---

## Ratchet

A completed task that introduces a regression in a previously-completed task is not actually complete.

**Detection.** When a `task.complete` event is appended, the harness:

1. Re-runs Layer 1 citation checks across **all complete-status tasks** for the project. Any citation that was valid and is now stale is flagged.
2. If any prior task's `consumes` list contains a citation whose hash changed because of the new task's outputs, the prior task is moved back to `blocked` via a `task.status` event.
3. The blocking event records `reason: ratchet <new-task> superseded <artifact>`.

The state engine drives this; the agent does not need to remember to check. A regression structurally cannot remain hidden because Layer 1 runs on every event and citation freshness is a calculation, not a judgment.

---

## Resume Without Session State

v4.1.1 maintained `SESSION-STATE.md` with per-step writes to support mid-task resume. v5.0 removes this. Resume is replay-based:

1. Read `events.jsonl` for events with `actor` matching the resuming agent or task.
2. The agent reconstructs context from the consumed-inputs projection (already up to date), the task instructions, and the most recent in-progress markers in events.
3. If a task was mid-step when interrupted, the projected state shows status `in_progress`; the agent re-runs from the last completed step inferred from events.

Step-level granularity is now derivable from the event log instead of written redundantly. Tasks that genuinely need finer granularity should be decomposed further, not given a parallel state file.

---

## Boundaries

| Positive | Enumerated by `consumes:`. The agent reads exactly these artifacts plus the rules file plus the task instructions. |
| Negative | Inferred from the absence in `consumes:`. The hermetic working set is the rule; "Do NOT Touch" is no longer authored manually. |

If the task genuinely needs to *write* outside its scope (e.g., to a shared deliverable), the planner declares it explicitly in `task.md` body. The frontmatter `consumes:` is read-only.

---

## Relationship to Other Mechanisms

| Mechanism | Interaction |
|---|---|
| Lock | Lock determines which project's TASK-STATE.yaml is active. |
| Typed Artifacts | `consumes:` cites artifacts; recitation projection lives at the task level. |
| Verification | Acceptance criteria run at Layer 2; risk level controls whether Layer 3 council fires. |
| Precedence | Tier 1 rules apply to every task regardless of `consumes:` (rules are not citation-gated). |
