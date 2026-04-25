# Substrate — Event-Sourced State

> **The substrate is not a mechanism.** It is the medium the five mechanisms compute against. Lock, Atomicity, Typed Artifacts, Verification, and Precedence are all primitives over event-sourced state. This file documents the layer they share.

---

## Hypothesis

| ID | Claim | Falsifier |
|---|---|---|
| H-S1 | A canonical append-only event log with regenerable projections eliminates the class of failure where two writers (agent + agent, or agent + operator) disagree about state because both edited a mutable file. | Two writers produce inconsistent state after both have written, with no event-log diff that distinguishes their contributions. |
| H-S2 | Hash-chained events make tampering and divergence structurally detectable. `hw verify` replay-with-hash produces ground-truth state reconstruction. | Tampering passes `hw verify`. |
| H-S3 | Projection regeneration means file corruption, partial saves, and manual edits are recoverable rather than catastrophic. | A corrupted projection cannot be restored from `events.jsonl` without manual reconstruction. |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  events.jsonl  (canonical)                  │
│    one immutable JSON line per event, hash-chained          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼  (projection regeneration)
┌─────────────────────────────────────────────────────────────┐
│   Projections  (regenerable, never authoritative)           │
│   • decisions/*.md         • findings/*.md                  │
│   • anti-patterns/*.md     • operating-reality/*.md         │
│   • TASK-STATE.yaml        • active_project.md              │
│   • backlog.md             • consumed-inputs.md  (per task) │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼  (sha256 of each projection)
┌─────────────────────────────────────────────────────────────┐
│   hashes.json  (sidecar, regenerable)                       │
│   maps each projection path → current sha256:<short>        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼  (versioning + worktree)
┌─────────────────────────────────────────────────────────────┐
│   git  (optional substrate-of-substrate)                    │
└─────────────────────────────────────────────────────────────┘
```

Canonical state lives in `events.jsonl`. Everything else is derived. If a projection diverges from what the events imply, the projection is wrong, not the events.

The **Mutable Surface** — narrative content authored by humans or agents (`PROJECT.md`, `00-REFERENCE-rules.md`, task instruction prose) — is canonical *as files*, not event-sourced. Narrative content has no useful event representation. The boundary between event-sourced (structured) and file-canonical (narrative) is declared per artifact kind in this file and in `core/TYPED-ARTIFACTS.md`.

---

## File Layout

```
.hyperworker/
  events.jsonl          # canonical event log
  hashes.json           # sidecar: projection path → current hash
  agents/               # subagent capability declarations
  models/               # active per-model profile (copied from templates/models/)
  config.yaml           # active project config (model profile, schema source)
projects/<id>/
  decisions/            # projections of decision events
  findings/             # projections of finding events
  anti-patterns/        # projections of anti-pattern events
  operating-reality/    # projections of operating-reality events
  tasks/<task-id>/
    consumed-inputs.md  # projection of recitation events for this task
```

`events.jsonl` lives once, in `.hyperworker/`, at the harness instance root. Projections live alongside the project content they belong to. One event log can drive projections in multiple project subdirectories.

---

## Event Format

Every event is one JSON line. Order is significant: events MUST be appended, never inserted, never deleted.

```json
{"id": "EV-0001", "ts": "2026-04-25T14:32:11Z", "kind": "decision.add", "actor": "executor:T-007", "project": "q3-launch", "payload": {...}, "prev_hash": "sha256:0000…", "hash": "sha256:a3f9…"}
```

**Required fields:**

| Field | Type | Meaning |
|---|---|---|
| `id` | string | `EV-<n>`, monotonically increasing, zero-padded to 4. |
| `ts` | string | ISO 8601 UTC timestamp. |
| `kind` | string | Dotted event kind (see Event Kinds below). |
| `actor` | string | `<role>:<id>` — `executor:T-007`, `planner`, `operator`, `council:reality-calibrator`. |
| `project` | string | Project ID this event belongs to, or `"_harness"` for harness-level events. |
| `payload` | object | Kind-specific structured data. |
| `prev_hash` | string | `hash` of previous event in the chain. First event uses `sha256:0000…`. |
| `hash` | string | `sha256:` of the canonical JSON serialization of `{id, ts, kind, actor, project, payload, prev_hash}`. |

**Hash computation.** The `hash` field is the SHA-256 of the line's JSON object with `hash` itself omitted, keys sorted lexicographically, and no whitespace. Truncate to 12 hex characters when displaying short form (`a3f9c2b1e0f4`). Full hash is recorded in the event line.

---

## Event Kinds

The harness defines a closed set. Schema extensions must add kinds via the project schema; the agent does not invent kinds.

### Project events

| Kind | Payload |
|---|---|
| `project.activate` | `{project_id, name, schema, started_at}` |
| `project.archive` | `{project_id, completed_at, summary}` |
| `project.park` | `{project_id, parked_at, reason}` |

### Backlog events

| Kind | Payload |
|---|---|
| `backlog.add` | `{entry_id, text, tags, priority, ts}` |
| `backlog.remove` | `{entry_id, reason}` |

### Typed-artifact events

| Kind | Payload |
|---|---|
| `decision.add` | `{artifact_id, fields...}` |
| `finding.add` | `{artifact_id, fields...}` |
| `anti-pattern.add` | `{artifact_id, fields...}` |
| `operating-reality.add` | `{artifact_id, fields...}` |
| `<kind>.supersede` | `{old_id, new_id, reason}` (emitted automatically when `<kind>.add` includes `reverses:`) |
| `<kind>.promote` | `{artifact_id, from: provisional, to: validated}` |

### Task events

| Kind | Payload |
|---|---|
| `task.create` | `{task_id, title, frontmatter}` |
| `task.status` | `{task_id, from, to}` |
| `task.recite` | `{task_id, consumed_id, paraphrase, overlap_score}` |
| `task.scan` | `{task_id, marker_id, answer}` |
| `task.complete` | `{task_id, completion_report_path}` |

### Branch / fold events

| Kind | Payload |
|---|---|
| `branch.open` | `{parent_task, branch_name}` |
| `branch.event` | `{parent_task, branch_name, sub_event_kind, sub_payload}` (sub-trajectory captured) |
| `branch.fold` | `{parent_task, branch_name, result_text}` |

### Verification events

| Kind | Payload |
|---|---|
| `verify.layer1.pass` / `verify.layer1.fail` | `{check_name, target_id, details}` |
| `verify.layer2.pass` / `verify.layer2.fail` | `{task_id, check_name, details}` |
| `council.invoke` | `{trigger, scope, members[]}` |
| `council.report` | `{member, role, finding, convergence_vote}` |
| `council.converged` / `council.escalated` | `{outcome, summary}` |

### Capability events

| Kind | Payload |
|---|---|
| `capability.gap` | `{task_id, agent_id, missing_tools[], gap_file_path}` |

---

## Projections

A projection is a regenerable file derived from events. Projections are **never authoritative**; they exist for human readability and for prompt-time loading.

### Projection rules

1. **Regenerable.** Any projection can be deleted and rebuilt from `events.jsonl` alone. If a projection cannot be reconstructed, the event schema is wrong.
2. **Idempotent.** Regenerating the same projection from the same event prefix produces byte-for-byte identical output.
3. **Hashed.** Every projection's current SHA-256 is recorded in `hashes.json` after each regeneration.
4. **Never hand-edited.** Editing a projection directly is operator error. The harness will overwrite on next regeneration. Operator-authored content goes in the Mutable Surface (see `core/ATOMICITY.md`).

### Projection table

| Projection | Source events | Path |
|---|---|---|
| Decision artifact | `decision.add`, `decision.supersede`, `decision.promote` | `projects/<id>/decisions/<artifact-id>.md` |
| Finding artifact | `finding.add`, `finding.supersede`, `finding.promote` | `projects/<id>/findings/<artifact-id>.md` |
| Anti-pattern artifact | `anti-pattern.add`, `anti-pattern.supersede` | `projects/<id>/anti-patterns/<artifact-id>.md` |
| Operating-reality artifact | `operating-reality.add`, `operating-reality.supersede` | `projects/<id>/operating-reality/<artifact-id>.md` |
| Task state | `task.create`, `task.status`, `task.complete`, dependency events | `projects/<id>/TASK-STATE.yaml` |
| Active project pointer | `project.activate`, `project.archive` | `projects/active_project.md` |
| Backlog | `backlog.add`, `backlog.remove` | `backlog.md` |
| Consumed inputs | `task.recite` events for one task | `projects/<id>/tasks/<task-id>/consumed-inputs.md` |
| Branch result | `branch.fold` | `projects/<id>/tasks/<task-id>/branches/<branch>/result.md` |

### Projection rendering

Each projection has a deterministic rendering protocol described in the relevant `core/*.md` file:

- Typed-artifact projections: `core/TYPED-ARTIFACTS.md`
- Task state projection: `core/ATOMICITY.md`
- Active-project + backlog projections: `core/LOCK.md`
- Consumed-inputs projection: `core/TYPED-ARTIFACTS.md` (Consumption Protocol)
- Branch result projection: `core/ATOMICITY.md`

A protocol is *complete* if a fresh agent can read the relevant `core/*.md` file plus this file and produce a byte-identical projection from a given event prefix. If two agents produce different output, the protocol has a gap; report it via `hw council` or operator escalation.

---

## Hash Sidecar (`hashes.json`)

`.hyperworker/hashes.json` is a single JSON object mapping projection paths to their current short hash:

```json
{
  "projects/q3-launch/decisions/DEC-007.md": "sha256:a3f9c2b1e0f4",
  "projects/q3-launch/findings/F-014.md":     "sha256:b8d4e1779a02",
  "projects/q3-launch/TASK-STATE.yaml":       "sha256:c1d2e3f4a5b6"
}
```

`hashes.json` is itself a projection: it is regenerated from `events.jsonl` and the projection rendering protocol. It is not authoritative.

---

## Citation Format

Every typed artifact is cited by `[<KIND>-<ID>#<short-hash>]` where short-hash is the first 12 hex characters of the artifact projection's SHA-256.

| Citation | Resolves to |
|---|---|
| `[DEC-007#a3f9c2b1e0f4]` | Current `decisions/DEC-007.md` if its hash matches; otherwise stale. |
| `[F-014#b8d4e1779a02]` | Current `findings/F-014.md`. |
| `[AP-005#…]` | Anti-pattern. |
| `[OR-001#…]` | Operating-reality. |

A citation is **valid** when the cited file exists and its current hash matches the cited short-hash. A citation is **stale** when the file exists but the hash differs (the artifact was superseded or re-projected). A citation is **broken** when the file does not exist.

Layer 1 verification (`core/VERIFICATION.md`) checks every citation in every event payload that lands in the log.

---

## The `hw` Command Set — Agent Protocol

`hw` is **not a CLI**. It is the name of an agent protocol. When this file or any other says `hw <command>`, it means: *the agent performs the operation defined here by reading and writing files directly.* No script is required, no installation is involved. Any agent that can read markdown and append to a file can execute `hw`.

Each operation below specifies: what to read, what to compute, what to write, what to validate. An agent that completes the steps in order produces the same effect as a hypothetical CLI would.

### `hw add <kind> < <file>`

Append a typed-artifact event and regenerate its projection.

**Inputs.** A draft markdown file containing the artifact's frontmatter (per the kind's schema in `schemas/artifacts/<kind>.yaml`) and its body.

**Steps.**
1. Read `schemas/artifacts/<kind>.yaml` and the project's `artifact-extensions.yaml` (if present). Validate the input file's frontmatter against the merged schema. If validation fails, abort with a structured error; do not write.
2. Determine `artifact_id`. If the input declares an `id`, use it (must be unique within kind). Otherwise generate the next ID for the kind: scan `events.jsonl` for `<kind>.add` events, find the highest numeric suffix, increment by one. Format: `<PREFIX>-<NNN>` where prefix is `DEC | F | AP | OR` for decision/finding/anti-pattern/operating-reality.
3. Read the last line of `events.jsonl`; let `prev_hash` be its `hash` (or `sha256:0000…0000` if the log is empty).
4. Build the event JSON object: `{id, ts, kind, actor, project, payload, prev_hash}` where `payload` contains the artifact frontmatter and body, and `id` is `EV-<next>`.
5. Compute `hash` per the Hash computation rule above. Append the full event line (with `hash`) to `events.jsonl`.
6. **Regenerate the artifact projection.** Render `projects/<project>/<kind>s/<artifact-id>.md` using the rendering protocol in `core/TYPED-ARTIFACTS.md`. The projection MUST be byte-identical to what a re-render from events would produce.
7. Compute the projection's SHA-256, take the first 12 hex chars, and update `hashes.json` for that path.
8. **Citation validation.** If the artifact body contains citations `[<KIND>-<ID>#<hash>]`, run Layer 1 citation checks (see `core/VERIFICATION.md` §Layer 1). Any broken or stale citation in the new artifact rejects the event — but the event is already appended. The harness emits `verify.layer1.fail` and immediately follows with a `<kind>.supersede` of the new event referring back to a `null` artifact (this records the rejection in the log; the projection is removed). The agent treats the original `hw add` as failed.
9. Report: artifact ID, short hash, and the citation form (`[KIND-ID#hash]`) that downstream tasks should use.

### `hw write <task-id> --status <state>`

Record a task state transition.

**Steps.**
1. Read the current task state from `TASK-STATE.yaml` (the projection). Find `<task-id>`. If the requested transition is not legal per the task state machine (`core/ATOMICITY.md`), abort.
2. Append `task.status` event with `{task_id, from, to}`. Compute hash, write to `events.jsonl`.
3. Re-render `TASK-STATE.yaml` per the protocol in `core/ATOMICITY.md` §Task State Projection. Update its hash in `hashes.json`.

### `hw branch <task-id> <branch-name>`

Open an exploratory subtask under a parent.

**Steps.**
1. Append `branch.open` event with `{parent_task, branch_name, ts}`.
2. Create `projects/<id>/tasks/<task-id>/branches/<branch-name>/` and copy `templates/task-template.md` into `task.md`. Set frontmatter `id: <parent-id>/<branch-name>`, `parent: <parent-id>`.
3. Open the branch's working context (a fresh agent or a fresh subagent context). The branch is its own atomic unit; see `core/ATOMICITY.md` §Branch / Fold.

### `hw fold <task-id>/<branch-name> --result <text>`

Collapse a branch back into the parent context, preserving sub-trajectory in events.

**Steps.**
1. Capture the branch's events: every event with `actor` matching `<branch-id>` since the matching `branch.open`. Wrap each as a `branch.event` payload of the parent.
2. Append `branch.fold` event with `{parent_task, branch_name, result_text}`.
3. Render `projects/<id>/tasks/<task-id>/branches/<branch-name>/result.md` containing only the `result_text` and a pointer to the branch event range. The full sub-trajectory is in the log; the projection is the 1–3 sentence summary the parent reads.
4. The parent context replaces its memory of the branch with the result projection on next read.

### `hw promote <artifact-id>`

Mark a typed artifact `confidence: validated`.

**Steps.**
1. Read the current projection for `<artifact-id>`. Confirm `confidence: provisional`. If already validated, no-op.
2. Append `<kind>.promote` event with `{artifact_id, from: provisional, to: validated}`.
3. Re-render the projection (the rendering protocol reads the latest event chain for the artifact and emits `confidence: validated`). Update its hash.

### `hw verify`

Replay the event log with hash-chaining and report integrity.

**Steps.**
1. Read `events.jsonl` line by line in order. For each event:
   - Recompute `hash` from its content. If recomputed hash ≠ recorded hash, record tamper.
   - If `prev_hash` ≠ previous line's `hash` (or `sha256:0000…` for the first line), record chain-break.
2. For each typed-artifact projection on disk, recompute its SHA-256 and compare with `hashes.json`. If they differ, record drift.
3. For each citation in any event payload (including artifact bodies), check valid / stale / broken.
4. Report: `OK` (all checks pass) or a structured failure list with event IDs, projection paths, and citation references involved.
5. `hw verify` does not repair. Repair is a separate agent operation: re-run the projection regeneration protocol for any drifted projection; investigate any tamper or chain-break before continuing.

### `hw project`

Force projection regeneration from events.

**Steps.**
1. Truncate `hashes.json` to `{}`.
2. For each typed-artifact ID present in events, render its projection from scratch using the protocol in `core/TYPED-ARTIFACTS.md`. Emit hash to `hashes.json`.
3. Render `TASK-STATE.yaml`, `active_project.md`, `backlog.md`, every `consumed-inputs.md`, every `branches/*/result.md`. Emit hashes.
4. Run `hw verify` and report.

### `hw bootstrap --schema <name> --name <project-id>`

Scaffold a project from a schema. See `core/LOCK.md` and §Bootstrap Protocol in `HARNESS.md`.

**Steps.**
1. Confirm no other project is currently active. If one is, refuse and require `hw park` or `hw wrap` first.
2. Read `schemas/projects/<name>/`. Copy structural files into `projects/<project-id>/`: `project-template.md → PROJECT.md`, `rules-template.md → 00-REFERENCE-rules.md`, `precedence-tiers.yaml → config-tiers.yaml`, `task-templates/* → tasks/*` (renumbered).
3. Append `project.activate` event.
4. Ask the operator only the schema-declared questions (operating reality fields, project description, specific rules content). For each operating-reality answer, run `hw add operating-reality` to write `OR-001`.
5. Trigger Verification Checkpoint with council. See `core/VERIFICATION.md` §Layer 3 and §8.4 Council Review.

### `hw schema save --from <project> --as <name>`

Extract a project's configurable substrate as a reusable schema.

**Steps.**
1. Read the project's tier configuration, schema extensions, capability gates, verification config, council composition, and task templates.
2. Strip project-specific content (specific decisions, findings, the operator's `OR-001`).
3. Write the result to `schemas/projects/<name>/`.

### `hw council <task-id>`

Manually invoke a council review. See `core/VERIFICATION.md` §Layer 3.

### `hw next-step`

Report the next pending task with all dependencies met.

**Steps.**
1. Read `TASK-STATE.yaml`.
2. Filter to `status: pending` tasks. Among those, filter to tasks whose `depends_on` are all `complete`.
3. Among remaining, prefer the lowest-numbered task ID. Report it.
4. If none, report blockers and the next council/checkpoint trigger.

### `hw status`

Report the current project state.

**Steps.** Read `active_project.md`, `TASK-STATE.yaml`, recent events. Summarize: active project, pending tasks count, blocked tasks, in-progress tasks, recent council outcomes, pending operator review.

### `hw log <text>`

Append to backlog without activating a project.

**Steps.**
1. Append `backlog.add` event with `{entry_id, text, ts}`. The agent assigns priority and tags from the text or asks the operator.
2. Re-render `backlog.md`.

### `hw wrap`

Run the project completion protocol.

**Steps.**
1. Confirm all tasks `complete` and acceptance criteria pass at Layer 2.
2. Run a discovery sweep over recent task events: any `verify.layer2.fail` retries, any `task.recite` rejections — flag for findings the operator may want to write.
3. Append `project.archive` event.
4. Re-render `active_project.md` to clear pointer; the archived project's projections remain in `projects/<id>/`.
5. Present top-three backlog entries from `backlog.md`.

### `hw park`

Demote the active project to backlog.

**Steps.**
1. Append `project.park` event with reason.
2. Re-render `active_project.md` (cleared) and `backlog.md` (with project re-listed).

---

## Git Integration (Optional)

If git is available:

- `events.jsonl` is committed automatically on every `hw add`, `hw write`, `hw branch`, `hw fold`, `hw promote`. Commit message: `<event-kind> <artifact-or-task-id>` (one event per commit).
- Projections are committed in the same commit as the event that produced them, so a repo at any commit reflects a consistent state.
- `hw branch` may use `git worktree` to give a delegated subagent context isolation. The worktree is removed on `hw fold`.
- `hw verify` additionally runs `git fsck` if available.

If git is unavailable, the harness still works: `events.jsonl` plus projection regeneration is sufficient. Git provides versioning and isolation; it is not load-bearing.

---

## Boundary Rule

Three categories of file:

| Category | Example | Authority |
|---|---|---|
| **Event-sourced (canonical)** | `events.jsonl` | Authoritative. Append-only. Never hand-edited. |
| **Projection (regenerable)** | `decisions/DEC-007.md`, `TASK-STATE.yaml`, `hashes.json` | Derived. Always regenerable from events. Never authoritative. |
| **Mutable Surface (file-canonical)** | `PROJECT.md`, `00-REFERENCE-rules.md`, `task.md` instructions, post-mortem prose | Authoritative as files. Versioned via git. Not event-sourced. |

A file is in exactly one category. If unsure, refer to the table in §File Layout. Editing across the boundary (writing to a projection, attempting to append narrative to `events.jsonl`) is operator error; the harness will overwrite or reject.

---

## Relationship to Mechanisms

| Mechanism | Substrate use |
|---|---|
| `core/LOCK.md` | `project.activate`, `project.archive`, `backlog.*` events; `active_project.md` and `backlog.md` projections. |
| `core/ATOMICITY.md` | `task.*`, `branch.*` events; `TASK-STATE.yaml`, branch result projections. |
| `core/TYPED-ARTIFACTS.md` | `<kind>.add`, `<kind>.supersede`, `<kind>.promote`, `task.recite` events; artifact projections; citations. |
| `core/VERIFICATION.md` | `verify.*`, `council.*` events; runs over the substrate, never bypasses it. |
| `core/PRECEDENCE.md` | Reads citations and substrate state to resolve rule conflicts; emits no events of its own. |
