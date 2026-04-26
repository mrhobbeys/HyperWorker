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

### File Locations (explicit)

The location convention is easy to misread when a project subdirectory feels like the more intuitive home for project-specific events. The substrate is workspace-scoped, not project-scoped.

| File | Location | Notes |
|---|---|---|
| `events.jsonl` | `.hyperworker/events.jsonl` at **workspace root** | Never under `projects/<id>/`. One log per workspace; events carry a `project` field for filtering. |
| `hashes.json` | `.hyperworker/hashes.json` at **workspace root** | Same scope as the event log. |
| `config.yaml` | `.hyperworker/config.yaml` at **workspace root** | Active model profile + schema source. |
| Per-project artifacts | `projects/<project-id>/decisions/`, `findings/`, etc. | Project-scoped projections. |
| Friction log (projection of `friction.log` events; v5.1+) | `friction-log.md` at **workspace root** by default; `projects/<project-id>/friction-log.md` if `friction_log_scope: project` in project config. The v5.0.1 working-artifact form (`bootstrap-friction-log.md`) is retained for pre-v5.1 projects but new projects emit events. | See §Friction Log Event Kind below and HARNESS.md §Friction Logs. |

If an agent reads from `projects/<id>/.hyperworker/events.jsonl`, that path is wrong. The event log is one level up.

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

**Hash computation.** The `hash` field is the SHA-256 of the line's JSON object with `hash` itself omitted, keys sorted lexicographically, and no whitespace, serialized per the Canonical Serialization rule below. Truncate to 12 hex characters when displaying short form (`a3f9c2b1e0f4`). Full hash is recorded in the event line.

---

## Canonical Serialization for Hashing

Every hash the harness computes — event hashes, projection hashes, citation short-hashes — uses the same canonical serialization. Two agents implementing the protocol independently MUST produce byte-identical hashes for the same input.

**The canonical form (Python reference idiom):**

```python
import json, hashlib
canonical = json.dumps(
    obj,
    sort_keys=True,
    separators=(',', ':'),
    ensure_ascii=False,
)
full_hash = hashlib.sha256(canonical.encode('utf-8')).hexdigest()
short_hash = full_hash[:12]
```

**Each option is load-bearing:**

| Option | Why |
|---|---|
| `sort_keys=True` | Two agents emitting the same fields in different insertion orders must produce the same bytes. |
| `separators=(',', ':')` | Python's default separators include trailing whitespace (`', '`, `': '`). Whitespace changes the bytes; whitespace changes the hash. |
| `ensure_ascii=False` | **Critical.** Python's `json.dumps` defaults to `ensure_ascii=True`, which escapes any non-ASCII character to `\uXXXX`. An agent writing `"voice": "résumé"` versus `"voice": "résumé"` produces divergent hashes for the same content. The first non-ASCII byte that lands in the log breaks chain integrity for every subsequent event if one agent escapes and another does not. UTF-8 source-of-truth, not ASCII-escaped JSON. |
| UTF-8 encoding before hashing | The hash is computed over the UTF-8 byte sequence of the canonical string. |

**Projection hashes.** A projection's hash is the SHA-256 of the projection file's bytes as written to disk (UTF-8, LF line endings). For citation purposes, the first 12 lowercase hex characters of the full hash are the short-hash recorded in `hashes.json` and used in `[KIND-NNN#hhhhhhhhhhhh]` citations.

**Full hash retained.** `events.jsonl` records the full SHA-256 hex string in each event's `hash` and `prev_hash` fields. The 12-character truncation is for citation display only; the hash chain itself is verified against full hashes.

Agents that re-implement the harness in non-Python environments must match this exact serialization. Use a JSON library that supports stable key ordering, ASCII-safe-off output, and minimal separators; if none is available, hand-roll the serializer. Do not skip this section.

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
| `council.invoke` | `{trigger, scope, members[], fire_id}` — `fire_id` is the `EV-NNNN` of the `council.invoke` event itself, used to group all `council.report` events for one fire. |
| `council.report` | `{fire_id, member, role, model_family, finding, convergence_vote}` — `fire_id` references the originating `council.invoke`; projection groups by it. See §Council Report Projection. |
| `council.converged` / `council.escalated` | `{fire_id, outcome, summary}` |

### Capability events

| Kind | Payload |
|---|---|
| `capability.gap` | `{task_id, agent_id, missing_tools[], gap_file_path}` |

### Friction events

| Kind | Payload |
|---|---|
| `friction.log` | `{type, patch_id, description, surfaced_by, severity, suggested_target}` — see §Friction Log Event Kind below for field semantics. |
| `friction.log.prompt` | `{trigger, task_id, signal_summary}` — informational; the harness emits this when an auto-prompt heuristic fires. The agent reads the prompt event and decides whether to follow it with an actual `friction.log` entry. |

### Session events

| Kind | Payload |
|---|---|
| `session.handoff` | `{project_id, closing_actor, last_completed_task, next_pending_task, active_artifact_state, open_operator_questions[], recommended_first_action, context_compaction_summary}` — see §Session Handoff Event Kind. One event per closing-session boundary; not chained. |

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
| Friction log | `friction.log` | `friction-log.md` at workspace root by default; `projects/<id>/friction-log.md` if `friction_log_scope: project` in project config. See §Friction Log Projection. |
| Council report (per fire) | `council.invoke`, `council.report`, `council.converged` / `council.escalated` (grouped by `fire_id`) | `projects/<id>/council/<fire_id>-<trigger>.md` |
| Council index | All council events for the project | `projects/<id>/council/INDEX.md` |
| Session handoff | `session.handoff` (most recent only) | `projects/<id>/SESSION-HANDOFF.md` |

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

Every typed artifact is cited by `[<KIND>-<NNN>#<hhhhhhhhhhhh>]` where:

- `<KIND>` is the artifact's prefix (`DEC`, `F`, `AP`, `OR`, plus any schema-declared prefixes such as `SRC`, `CLM`, `CTR`).
- `<NNN>` is the zero-padded numeric ID (minimum 3 digits, may grow as IDs exceed 999).
- `<hhhhhhhhhhhh>` is the first **12 lowercase hex characters** of the SHA-256 of the artifact projection. Truncation length is fixed at 12; agents MUST NOT use a different length. The full SHA-256 is in `hashes.json`.

| Citation | Resolves to |
|---|---|
| `[DEC-007#a3f9c2b1e0f4]` | Current `decisions/DEC-007.md` if its hash matches; otherwise stale. |
| `[F-014#b8d4e1779a02]` | Current `findings/F-014.md`. |
| `[AP-005#c1d2e3f4a5b6]` | Anti-pattern. |
| `[OR-001#d2e3f4a5b6c7]` | Operating-reality. |
| `[SRC-003#…]`, `[CLM-042#…]`, `[CTR-001#…]` | Schema-declared kinds (e.g., report-synthesis). |

A citation is **valid** when the cited file exists and its current short-hash matches the cited 12-hex string. A citation is **stale** when the file exists but the short-hash differs (the artifact was superseded or re-projected). A citation is **broken** when the file does not exist.

Layer 1 verification (`core/VERIFICATION.md`) checks every citation in every event payload that lands in the log.

Templates and protocols throughout this repo use this exact form. When a template shows `[OR-001#<short-hash>]`, the executor substitutes the current 12-hex short-hash from `hashes.json` at the moment the citation is written.

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

Replay the event log with hash-chaining and report integrity. `hw verify` is a protocol; an agent executes it by reading and writing files. A reference Python implementation ships at `tools/hw-verify.py` — agents may reimplement for their environment, but the canonical algorithm and result format below are authoritative.

**Algorithm.**

1. **Read events.** Open `.hyperworker/events.jsonl`. Read line by line in append order. For each line, parse as JSON.
2. **Recompute event hash.** For each event:
   - Build the canonical object: every field of the event *except* `hash`. Specifically: `{id, ts, kind, actor, project, payload, prev_hash}`.
   - Serialize per the §Canonical Serialization rule (`json.dumps(obj, sort_keys=True, separators=(',',':'), ensure_ascii=False)`).
   - Compute SHA-256 of the UTF-8-encoded serialization.
   - Compare with the recorded `hash`. If they differ, record `tamper(EV-NNNN)`.
3. **Verify chain integrity.** For each event after the first, check that its `prev_hash` equals the previous line's recorded `hash`. The first event's `prev_hash` MUST be the all-zeros sentinel (`sha256:0000…0000` or the equivalent 64-zero hex string). Mismatch records `chain-break(EV-NNNN)`.
4. **Verify projection hashes.** For every entry in `.hyperworker/hashes.json`:
   - Read the file at the projection path.
   - Compute SHA-256 of its bytes; take the first 12 lowercase hex chars.
   - Compare with the recorded short-hash. Mismatch records `drift(<projection-path>)`.
   - Missing file (path in `hashes.json` but no file on disk) records `missing-projection(<path>)`.
   - Conversely, scan `projects/*/decisions/`, `findings/`, `anti-patterns/`, `operating-reality/`, `<schema-kinds>/` for projection files not represented in `hashes.json`. Each records `untracked-projection(<path>)`.
5. **Verify citations.** For each citation `[KIND-NNN#hhhhhhhhhhhh]` appearing in any event payload (artifact body, completion-report content, decision rationale, etc.):
   - **Broken** if no projection file exists for `KIND-NNN`.
   - **Stale** if the projection exists but its current short-hash differs from the cited one. (A stale citation may indicate the cited artifact was superseded; verify against the supersede chain before flagging as a defect.)
   - **Valid** otherwise.
6. **Emit result.** Structured report:

```
hw verify <workspace>:
  events_scanned:        <N>
  tamper:                <count> [<list of EV-IDs>]
  chain_breaks:          <count> [<list of EV-IDs>]
  projection_drift:      <count> [<list of paths>]
  missing_projections:   <count> [<list of paths>]
  untracked_projections: <count> [<list of paths>]
  broken_citations:      <count> [<list of citations + event-IDs>]
  stale_citations:       <count> [<list of citations + event-IDs>]
  result:                PASS | FAIL
```

`PASS` requires zero entries in tamper, chain_breaks, projection_drift, missing_projections, broken_citations. Stale citations are reported but do not block PASS; a stale citation is information, not corruption (the supersede chain may explain it).

`untracked_projections` is reported as a warning, not a FAIL — operators may have added local files; the next `hw project` will reconcile.

**Incremental verification.**

`hw verify --since=EV-NNNN` skips the chain re-walk for events before `EV-NNNN`. Steps:

1. Read events.jsonl until reaching the line with `id == EV-NNNN`. Use that event's recorded `hash` as the starting `prev_hash` baseline. Trust the prefix.
2. Run steps 2-3 from `EV-(NNNN+1)` onward.
3. Run steps 4-5 over the **entire** projection set and **all** citations (incremental cannot skip these; a stale citation in an old event payload is a current defect).

Use `--since` for routine post-task checks where the prior chain is known-good (typically the event ID emitted by the last successful `hw verify`).

`hw verify` does not repair. Repair is a separate agent operation: re-run the projection regeneration protocol for any drifted projection (or run `hw project`); investigate any tamper or chain-break before continuing — do not "fix" a tamper by rewriting `hash` fields.

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
2. Read `schemas/projects/<name>/`. Copy structural files into `projects/<project-id>/`:
   - `project-template.md → PROJECT.md`
   - `rules-template.md → 00-REFERENCE-rules.md`
   - `precedence-tiers.yaml → config-tiers.yaml`
   - `task-templates/<filename>.md → tasks/<filename>.md` — **filenames copied verbatim**, frontmatter `id` fields preserved (e.g., `task-templates/00-source-inventory.md` becomes `tasks/00-source-inventory.md` with `id: T-000` intact). The earlier "renumbered" wording was misleading: nothing is renumbered. Filenames and IDs are stable across the copy. Schema-declared task IDs are the canonical handles tasks reference each other by.
3. Create the operator-declared input/work folder if the schema declares one (e.g., report-synthesis declares `input_folder` in its bootstrap questions). If the folder already exists, leave its contents untouched. Bootstrap is responsible for the folder's existence; tasks downstream assume it exists.
4. Append `project.activate` event.
5. Ask the operator only the schema-declared questions (`schema.yaml` `bootstrap_questions`). For each operating-reality answer, run `hw add operating-reality` to write `OR-001`. If the schema's `bootstrap_questions` does not cover every base operating-reality field declared in `templates/artifact-templates/operating-reality-template.md`, the schema's `artifact-extensions.yaml` MUST mark those fields optional or override their defaults; otherwise the operator is asked the missing fields explicitly.
6. Trigger Verification Checkpoint with council. See `core/VERIFICATION.md` §Layer 3 and §8.4 Council Review.

**Mid-bootstrap corrections.** If the operator corrects an OR field after the first `operating-reality.add`, the correction is event-sourced as a supersede: `hw add operating-reality` for `OR-002` with `reverses: OR-001`. There is no in-place edit. Two-minute-old artifacts are valid supersede targets — the supersede chain captures the correction history with no special handling. See §Superseded Artifact Back-Link below for how the older projection is updated.

**Mid-bootstrap structural directives.** If the operator issues an instruction that doesn't fit `bootstrap_questions` (e.g., "use the browser when needed", "Example Corp IT and Example Corp are separate companies"), capture it as a typed Decision artifact with an appropriate `synthesis_role` (or schema-equivalent), not as loose conversation. Loose-prose directives that affect project structure are unverifiable; typed Decisions are citable, hash-verified, and become consumed-input for downstream tasks. See HARNESS.md §Bootstrap Protocol for the canonical pattern.

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
| **Projection (regenerable)** | `decisions/DEC-007.md`, `TASK-STATE.yaml`, `hashes.json`, `friction-log.md`, `SESSION-HANDOFF.md`, `council/<fire>-<trigger>.md` | Derived. Always regenerable from events. Never authoritative. |
| **Mutable Surface (file-canonical)** | `PROJECT.md`, `00-REFERENCE-rules.md`, `task.md` instructions, post-mortem prose | Authoritative as files. Versioned via git. Not event-sourced. |

A file is in exactly one category. If unsure, refer to the table in §File Layout. Editing across the boundary (writing to a projection, attempting to append narrative to `events.jsonl`) is operator error; the harness will overwrite or reject.

---

## Superseded Artifact Back-Link

When artifact `B` supersedes artifact `A` (i.e., a `<kind>.add` event creates `B` with `reverses: A`), the harness emits a `<kind>.supersede` event automatically (see §Event Kinds). The supersede event MUST trigger a re-render of artifact `A`'s projection so that `A`'s frontmatter carries `superseded_by: [B-NNN#hhhhhhhhhhhh]` referencing the superseding artifact's current short-hash.

**Rendering rule.** The projection for `A` is regenerated using the standard protocol in `core/TYPED-ARTIFACTS.md` §Projection Rendering Protocol, with the additional step:

- If any later event in the chain is a `<kind>.supersede` whose `payload.old_id == A`, set `superseded_by: [<new_id>#<short-hash-of-new-projection>]` in `A`'s frontmatter. Else `superseded_by: null`.

This means a re-render of `A` happens twice in the typical flow: once when `A` is first added, and once when `B` (its superseder) is added. The hash of `A`'s projection changes on the second render — citations to the original `A#hash` become stale, which is the correct signal: anything still citing `A` should review whether it should now cite `B`.

**Hash update propagation.** When `A`'s projection re-renders, `hashes.json` is updated for `A`'s path. Any cached `[A#oldhash]` citation in subsequent events becomes stale at Layer 1 verification — visible, recoverable.

The supersede chain remains traversable forward (`A.superseded_by → B`) and backward (`B.reverses → A`).

---

## null vs `[]` for Empty-Set Fields

Several artifact fields accept lists (`tags`, `excluded_topics`, `alternatives_considered`, etc.). The substrate distinguishes two semantically distinct empty states:

| Value | Meaning |
|---|---|
| `[]` | Declared as empty. The operator (or agent) explicitly considered the field and confirmed there is nothing to list. |
| `null` | Not declared, or not applicable. The field's content is unknown or the field does not apply to this artifact. |

**Schema validation enforces the distinction.** A schema field declared `type: list[string]` (no `\|null`) requires `[]` as the empty form; `null` fails validation. A field declared `type: list[string]\|null` accepts both, and the value carries semantic weight: `excluded_topics: []` means "the operator confirmed nothing is out of scope," `excluded_topics: null` means "we did not ask."

**Canonical serialization implication.** `[]` and `null` serialize to different JSON bytes, so they hash differently. An agent that defaults a missing-but-confirmed-empty field to `null` produces a different artifact hash than one that uses `[]`. When in doubt, prefer `[]` for confirmed-empty (the common case after asking the operator) and `null` for confirmed-not-applicable.

When converting operator answers like "None", "no", or an empty operator response, the canonical form is `[]` (the operator answered the question; the answer was empty). `null` is reserved for fields the harness or operator did not address.

---

## Lightweight Completion (Optional Task Frontmatter)

A task template may declare `lightweight_completion: true` in its frontmatter. When set, the task's completion report is a 3-line summary instead of the full template (acceptance criteria result, outputs produced, follow-up note). The `task.complete` event still emits with `completion_report_path`, the report file still lands in `tasks/<task-id>/`, but the body is a 3-bullet summary. Layer 2 still runs.

Use for mechanical tasks where the event log itself captures the substantive state — anti-pattern extraction from supersede chains, declarative structure decisions, mechanical inventories. Do not use for elevated/critical risk tasks; the full completion report is required where the report carries non-obvious state (acceptance criteria for ambiguous criteria, failure scenarios, council outcomes).

The flag is locked at task authoring; an executor cannot opt into a lightweight completion mid-task.

---

## Friction Log Event Kind

`friction.log` makes friction capture a substrate event, not an operator-instructed prose habit. The closing v5.0 lead-magnet run lost real-time friction signal because the agent did not follow a verbal prompt to capture it. v5.1 makes the harness do the prompting and the recording.

**Payload schema.**

| Field | Type | Meaning |
|---|---|---|
| `type` | enum | `REGRESSION`, `CONFIRMATION`, `NEW-SCHEMA`, `NEW-CROSS`, `TRAINING-FILL`, `OPERATOR-CONFUSION`. The category the friction maps to in the patch-cycle vocabulary. |
| `patch_id` | string \| null | The harness patch ID this friction targets if known (e.g., `B-1`); otherwise `null`. |
| `description` | string | 1-3 sentences. Specific enough that a future patch author can decide whether the friction has been addressed. |
| `surfaced_by` | string | `operator`, `executor:T-NNN`, `council:<role>`, or `harness` (substrate auto-detected). |
| `severity` | enum | `blocking`, `non-blocking`. Blocking means the agent could not proceed without the operator resolving the friction; non-blocking means it was visible but did not stop work. |
| `suggested_target` | enum \| null | `v5.x-doc-patch`, `v5.x-substrate`, `schema-specific`, or `unclear`. The agent's best guess at what kind of fix this needs. |

**Auto-prompt heuristics.** The harness emits a `friction.log.prompt` event (informational; agent decides whether to follow it with an actual `friction.log`) when any of the following observable signals fire:

| Signal | Detection |
|---|---|
| Layer 1 verification fails on the same check ≥3 times within a single task | Count `verify.layer1.fail` events with the same `check_name` and `target_id` since the most recent `task.create` of the active task. |
| Layer 2 verification fails | Any `verify.layer2.fail` event. |
| Agent output contains training-fill markers | Substring match in the most recent state-changing event's payload string fields against the marker set: `"I'm assuming"`, `"Based on common practice"`, `"The harness doesn't specify so"`, `"Typically..."`, `"In most cases..."`. Heuristic; agent decides if it actually crossed the bar. |
| Operator emits a mid-flow directive captured as a Decision artifact | A `decision.add` event with `actor: operator` and a `synthesis_role` (or schema-equivalent) that maps to mid-flow directive (e.g., `scope-decision`, `weighting-rule`, `inclusion-exclusion`) within an active project. |
| Council non-convergence on a critical-risk task | A `council.escalated` event whose triggering task has `risk_level: critical`. |

The auto-prompt heuristics above are starting points. The false-positive rate is unknown until v5.1 sees real use. Operators tune by observing how often `friction.log.prompt` events lead to genuine `friction.log` entries vs. agent-rejected noise; if the false-positive rate is high, the heuristic that produces the noise is the candidate for revision.

**`friction.log.prompt` payload.** `{trigger, task_id, signal_summary}` where `trigger` is the heuristic name from the table above, `task_id` is the active task at the time of the signal (or `null` for between-task signals), and `signal_summary` is a one-line description of what the heuristic observed.

**Agent response to a prompt.** When a `friction.log.prompt` lands, the agent reads it on its next turn and decides:

1. The signal was a real friction → the agent appends a `friction.log` event with the appropriate payload.
2. The signal was a false positive → the agent does nothing (no event); the `friction.log.prompt` remains in the log as evidence the heuristic fired but was rejected, which itself is signal for tuning.
3. The signal is ambiguous → the agent surfaces a one-sentence question to the operator at the next natural pause.

**Friction Log Projection.** The projection at `friction-log.md` (workspace root by default; `projects/<id>/friction-log.md` if the project's `config.yaml` declares `friction_log_scope: project`) regenerates from `friction.log` events on each new event. Format:

```markdown
# Friction Log — <workspace-or-project-name>

> Regenerable from `friction.log` events. Operator and agent observations of harness friction. Hand-edits are overwritten on next regeneration; capture additions via `friction.log` events.

## Active

### F-NNN — <type>: <description first line>

- **Patch ID:** <patch_id or "unclassified">
- **Severity:** <blocking | non-blocking>
- **Surfaced by:** <surfaced_by>
- **Suggested target:** <suggested_target>
- **Event:** EV-NNNN
- **Description:** <full description>

## Resolved

(Friction entries whose `suggested_target` patch landed in a later harness version, marked resolved by a follow-up `friction.log` event with `type: CONFIRMATION` and `patch_id` referencing the original.)
```

Friction entries are append-only; resolution is a new entry, not an edit. The projection groups Active entries (no resolution) and Resolved entries (a CONFIRMATION entry exists referencing this entry's `patch_id`).

---

## Council Report Projection

A council fire is a logical group: one `council.invoke` event, N `council.report` events (one per member), and one terminal `council.converged` or `council.escalated`. `council.invoke.fire_id` is `EV-NNNN` of the invoke event itself — every report and the terminal event reference it via the `fire_id` payload field.

**Per-fire projection.** For each `council.invoke` event, the harness regenerates `projects/<id>/council/<fire_id>-<trigger>.md`. The `<trigger>` token in the filename is the trigger event kind (e.g., `project.activate`, `phase.complete`, `task.complete`, `hw_council`). One file per fire; the file is overwritten when any of its constituent events change (rare; events are append-only, so the file changes only on supersedes).

Format:

```markdown
# Council Fire — <fire_id> (<trigger>)

- **Trigger event:** <event-id-of-the-event-that-fired-the-council> (<kind>)
- **Invoked at:** <ts of council.invoke>
- **Subject under review:** <artifact-id, task-id, or phase-id>
- **Convergence rule:** <all-agree-or-escalate | majority-or-escalate | any-fail-blocks>

## Members

| Role | Model family | Verdict | One-line summary |
|---|---|---|---|
| <role-1> | <model_family> | PASS \| FAIL | <one-line summary from finding> |
| <role-2> | <model_family> | ... | ... |

## Outcome

- **Result:** converged \| escalated
- **Outcome event:** EV-NNNN
- **Operator action taken:** <if any operator-recorded follow-up exists> | none

## Detail

For each member, the full finding text is included verbatim from the `council.report` payload, in case the one-liner does not capture the basis for the verdict.
```

The full chain-of-thought of a council member is **not** included in the projection by design; council members run with context-asymmetric framing and their reasoning is not operator-readable in real time. The `finding` text in the report is the member's externalized output; that is what the projection surfaces.

**Aggregate projection (`INDEX.md`).** `projects/<id>/council/INDEX.md` lists all fires chronologically:

```markdown
# Council Fires — <project-id>

| Fire | Trigger | Subject | Outcome | Date |
|---|---|---|---|---|
| [EV-0042](EV-0042-project.activate.md) | project.activate | OR-001 | converged | 2026-04-26T10:14Z |
| [EV-0117](EV-0117-phase.complete.md) | phase.complete (B) | claims-corpus | escalated | 2026-04-26T15:32Z |
| ... | ... | ... | ... | ... |
```

Both projections are regenerated on every council event. `hashes.json` tracks each per-fire file plus `INDEX.md`.

**Why both per-fire and aggregate.** The per-fire file is the one an operator opens when reviewing what a specific council found. The aggregate is the one an operator opens when answering "did council fire on this project at all, and where." The two together let the operator answer both questions without grepping `events.jsonl`.

**Backward-compat fallback for `fire_id`.** v5.0.1 council events (`council.invoke`, `council.report`, `council.converged`, `council.escalated`) pre-date the `fire_id` payload field. The projection generator handles this case structurally: when grouping `council.report` events into a per-fire projection, the generator looks for `fire_id` in the payload first; if absent, it reverse-scans `events.jsonl` from the report event's position to find the most recent `council.invoke` event in the same `project` whose trigger window has not yet been closed by a `council.converged` or `council.escalated`, and uses that invoke event's `id` as the grouping key. The same fallback applies to the terminal `council.converged` / `council.escalated` events. v5.1+ events emit `fire_id` directly and skip the reverse scan; v5.0.1 events fall back. `hw verify` does not require `fire_id` on any council event for the same reason — the field is recommended for new events, not required for replay integrity.

---

## Session Handoff Event Kind

Long projects span sessions; v5.0/v5.0.1 used informal `SESSION-HANDOFF.md` prose authored by the closing agent. The next agent might or might not read it. v5.1 makes handoff a substrate event so the resuming agent has a structural anchor that survives session boundaries by replay.

**Payload schema.**

| Field | Type | Meaning |
|---|---|---|
| `project_id` | string | The active project at handoff. |
| `closing_actor` | string | Closing agent identity (model name + session/turn count if known). |
| `last_completed_task` | string \| null | `T-NNN` of the most recently `task.complete` task for this project. |
| `next_pending_task` | string \| null | `T-NNN` `hw next-step` would select if run now. |
| `active_artifact_state` | object | `{decisions_count, findings_count, anti_patterns_count, contradictions_open}`. `contradictions_open` is reported only for synthesis-schema projects; other schemas may emit `0` or omit. |
| `open_operator_questions` | list[string] | Questions the closing agent did not resolve. The resuming agent MUST acknowledge each before its first state-changing event in the session. |
| `recommended_first_action` | string | One concrete action the closing agent recommends the resuming agent take first. |
| `context_compaction_summary` | string \| null | If the closing agent's context filled and compacted, a brief summary of what was compacted. `null` if no compaction occurred. |

**Projection.** `projects/<id>/SESSION-HANDOFF.md` is overwritten on each `session.handoff` event. Handoffs are per-session; a new event entirely replaces the prior projection. The projection format follows `templates/session-handoff-template.md`. The hash sidecar tracks the file as usual.

**Resume behavior.** A task template MAY declare `requires_handoff_acknowledge: true` in its frontmatter. When set, the executor MUST, before its first state-changing event:

1. Read `projects/<id>/SESSION-HANDOFF.md` if present.
2. For each entry in `open_operator_questions`, either resolve it (record the resolution in the task's working log and proceed) or surface it to the operator (record a `task.status → blocked` with `reason: handoff_open_question <question>`).

The default for new task templates is unset (`false`); schemas that benefit from explicit handoff acknowledgement (long synthesis runs, multi-week projects) set it on the relevant T-* templates.

**Why this is structural.** The projection isn't authoritative; the event is. If the resuming agent paraphrases the handoff incorrectly, replay reproduces the original handoff event and the divergence is visible. The acknowledgement requirement is enforced by the task template (frontmatter field), not by verbal request — Layer 1 inspects the requirement at task start and blocks if no acknowledgement appears in the task's events before the first state-changing event.

---

## Relationship to Mechanisms

| Mechanism | Substrate use |
|---|---|
| `core/LOCK.md` | `project.activate`, `project.archive`, `backlog.*` events; `active_project.md` and `backlog.md` projections. |
| `core/ATOMICITY.md` | `task.*`, `branch.*` events; `TASK-STATE.yaml`, branch result projections. |
| `core/TYPED-ARTIFACTS.md` | `<kind>.add`, `<kind>.supersede`, `<kind>.promote`, `task.recite` events; artifact projections; citations. |
| `core/VERIFICATION.md` | `verify.*`, `council.*` events; council projections; runs over the substrate, never bypasses it. |
| `core/PRECEDENCE.md` | Reads citations and substrate state to resolve rule conflicts; emits no events of its own. |
| Friction logging | `friction.log`, `friction.log.prompt` events; `friction-log.md` projection. Spans mechanisms — any mechanism may surface a friction. |
| Session continuity | `session.handoff` events; `SESSION-HANDOFF.md` projection. Read by Atomicity at task start when `requires_handoff_acknowledge: true`. |
