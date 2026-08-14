# Substrate — Event-Sourced State

> **The substrate is not a mechanism.** It is the medium the five mechanisms compute against. Lock, Atomicity, Typed Artifacts, Verification, and Precedence are all primitives over event-sourced state. This file documents the layer they share. Read it once before the first bootstrap; reread the §`hw verify` and §Canonical Serialization sections any time `hw verify` returns FAIL.

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

### Deriving the Next Event ID

**The next event ID is the chain tail's ID plus one. Nothing else is an input.**

Read the last line of `.hyperworker/events.jsonl` — the same line `hw add` already reads to get `prev_hash` — parse its `id`, increment. One read, one source, one answer.

Never derive the next ID from project-scoped state: not the last event carrying this project's `project` field, not `TASK-STATE.yaml`, not a projection, not a session handoff, and not the agent's own memory of what it last wrote. `events.jsonl` is workspace-scoped (§File Locations); the ID sequence is a property of the log, not of any project inside it. A project-scoped derivation is correct only in the degenerate case where the workspace holds exactly one project and exactly one writer, and it fails silently the moment either stops being true.

**The field incident (2026-07, ten-week deployment).** Two agents worked one workspace. The resuming agent computed its next ID from the last event *of its own project* rather than from the chain tail, and appended `EV-0116` through `EV-0120` — IDs the other agent had already used, with entirely different content. Every one of the ten events had a correct `prev_hash` (each was appended to the real tail), so hash-chain verification found nothing wrong and `hw verify` returned **PASS** on a log holding ten events under five names. The chain was intact; the identifiers were not, and nothing checked them.

Two things follow, and both now exist as code rather than as this paragraph:

- Event IDs are unique across the whole log, and strictly increasing in append order. Duplicate IDs, or an ID no greater than one already seen, are Layer 1 FAILs (`duplicate_event_id`, `non_monotonic_event_id`; see `core/VERIFICATION.md` §Layer 1 check 14). The duplicate report names both line numbers, actors, and projects, because deciding which of two same-named events to keep is a human judgment about content that the verifier cannot make.
- Gaps are legal. IDs must increase; they need not be contiguous. A verifier that demanded contiguity would reject a legitimately truncated or `--since`-verified prefix.

Note that this is the *identifier* half of the Single-Writer Rule below. The rule prevents the collision; this check detects it when the rule was not followed.

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
| `finding.add` | `{artifact_id, fields..., claim?}` — `claim` is an optional §Checked Claims (v5.3) block; required per-schema via `verification.yaml` `checked_claims.required_for`. A finding used as a hypothesis may also carry `status` and `test_ref`; see §Exclusion Discipline (v6.0.0). |
| `anti-pattern.add` | `{artifact_id, fields...}` |
| `operating-reality.add` | `{artifact_id, fields...}` |
| `<kind>.supersede` | `{old_id, new_id, reason, supersede_kind, surviving_principles}` (emitted automatically when `<kind>.add` includes `reverses:`; one supersede event per reversed artifact when `reverses:` is a list). `supersede_kind` ∈ `{full, mechanism-only, scope-narrowing}`, default `full`. `surviving_principles` is a list of verbatim principles from the old artifact that remain load-bearing (`[]` for `full`) — so a fresh agent reading the chain can distinguish "this decision is dead, ignore it" from "its mechanism changed but its principle still binds." (v5.3; both fields optional on pre-v5.3 chains.) |
| `<kind>.promote` | `{artifact_id, from: provisional, to: validated}` |

### Task events

| Kind | Payload |
|---|---|
| `task.create` | `{task_id, title, frontmatter}` |
| `task.status` | `{task_id, from, to}` |
| `task.recite` | `{task_id, consumed_id, paraphrase, overlap_score}` |
| `task.scan` | `{task_id, marker_id, answer}` |
| `task.complete` | `{task_id, completion_report_path, claim?}` — `claim` is optional; see §Checked Claims (v5.3). |

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
| `friction.log` | `{note}` required; `{category, severity, task_id}` optional. One line, one event (v6.0.0). The pre-v6 rich form `{type, patch_id, description, surfaced_by, severity, suggested_target}` is still accepted. See §Friction Log Event Kind. |
| `friction.log.prompt` | `{trigger, task_id, signal_summary}` — informational; the harness emits this when an auto-prompt heuristic fires. The agent reads the prompt event and decides whether to follow it with an actual `friction.log` entry. |

### Session events

| Kind | Payload |
|---|---|
| `session.handoff` | `{project_id, closing_actor, last_completed_task, next_pending_task, active_artifact_state, open_operator_questions[], recommended_first_action, context_compaction_summary}` — see §Session Handoff Event Kind. One event per closing-session boundary; not chained. |
| `scope.complete` | `{scope_items: [{id, name, terminal_state, reason, claim?}]}` — see §Scope Completeness. Emitted before `session.handoff`; Layer 1 cross-checks against PROJECT.md §Scope. `scope_items[].claim` is optional; see §Checked Claims (v5.3). |

### Evidence events (v6.0.0)

| Kind | Payload |
|---|---|
| `evidence.capture` | `{id, producing_command, captured_at, content \| (content_path + content_sha256), summary}` — `id` is `ED-NNN`, unique across the log. The raw output of a load-bearing command, kept. See §Evidence Capture. |

### External-state events

| Kind | Payload |
|---|---|
| `external_state.read_back` | `{task_id, artifact_url, pre_state_ref, post_state_ref, equality_method, divergence_detected, divergence_notes, claim?}` — see §External State Read-Back. Per-schema opt-in via `capability-gates.yaml` `external_state_readback.required_for`. `claim` is optional; see §Checked Claims (v5.3). |

### Bootstrap events

| Kind | Payload |
|---|---|
| `bootstrap.inventory_diff` | `{schema, probe_method, declared, found, missing_from_declared, missing_from_found, operator_reconciliation}` — see §Bootstrap Inventory Sweep. |
| `bootstrap.scope_locked` | `{project_id, locked_at, scope_items[]}` — closes the inventory sweep ceremony after operator reconciliation. |
| `bootstrap.probe_skipped` | `{schema, reason}` — alternative ceremony close when no probe ran (e.g., schema's probe is stubbed). |

### Operator-identity events (v5.2.0)

| Kind | Payload |
|---|---|
| `operator_soul_anchor` | `{soul_path, soul_hash, version, fired_at}` — see §Operator Soul Anchor. Fired at bootstrap when the operator's soul.md exists. Mirrors the `brand_voice_anchor` pattern: anchors a Phase B task's first state-changing event behind the existence of the anchor on the log. |

### Toolchain events (v5.2.1)

| Kind | Payload |
|---|---|
| `toolchain.anchor` | `{tools: [{name, path, sha256}], source, spec_version, fired_at}` — see §Toolchain Anchor. Pins the hash of every script the agent will use for hash-computing operations. `source` ∈ `{shipped, generated}`. Re-anchoring on deliberate tool change is a new event; silent drift is a Layer 1 FAIL. |

### Lifecycle events (v5.3)

Valid only on a project whose `PROJECT.md` declares `lifecycle: ongoing` (see `core/LOCK.md` §Ongoing Projects). On a terminal-lifecycle project, emitting either kind is a Layer 1 FAIL.

| Kind | Payload |
|---|---|
| `cycle.open` | `{project_id, cycle_id, opened_at, cadence}` — `cycle_id` is `C-NNN`, monotonic per project. `cadence` is recorded verbatim from `OR-001` (e.g., `"weekly"`, `"P7D"`, a cron expression) plus a normalized `cadence_days: <int>` the harness computes once at bootstrap so due-date math never re-parses prose. |
| `cycle.close` | `{project_id, cycle_id, closed_at, summary, next_due}` — `next_due` (`YYYY-MM-DD`) is computed at close as `closed_at + cadence_days` and recorded **on the event**, so "when is the next sweep due" is substrate state, not prose in a handoff. A close without a matching open, or a second open without an intervening close, is a Layer 1 FAIL. |

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
| Cycle index (ongoing projects) | `cycle.open`, `cycle.close` | `projects/<id>/CYCLES.md` — one row per cycle: id, opened, closed, summary, next_due. Format and rendering protocol: `templates/CYCLES.md`. The `active_project.md` projection additionally carries `Next due:` for an ongoing active project. |
| Evidence capture (v6.0.0) | `evidence.capture` | `projects/<id>/evidence/<ED-NNN>.md` — one file per capture. Format: `templates/artifact-templates/evidence-capture.md`. See §Evidence Capture. |
| Elimination matrix (v6.0.0) | `finding.add` / `finding.supersede` events whose payload carries `status` | `projects/<id>/ELIMINATION.md` — frontier line plus one row per hypothesis: hypothesis, status, how-tested, result. Format and rendering protocol: `templates/ELIMINATION.md`. See §Exclusion Discipline. |

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
3. **Citation validation (pre-append).** If the artifact body contains citations `[<KIND>-<ID>#<hash>]`, run Layer 1 citation checks (see `core/VERIFICATION.md` §Layer 1) against the current `hashes.json` *before* anything is written. Any broken or stale citation aborts with a structured error naming the citation and the artifact's current short-hash; nothing lands in the log. The agent corrects the citation and retries. (Changed in v5.2.1: earlier versions appended the event first and reversed it with a supersede-to-null, leaving a rejection pair in the chain for every mistyped citation. Citation checking is a read-only computation; there is no reason to dirty the log to perform it. The supersede-to-null path remains only for defects discovered *after* append — see `core/VERIFICATION.md` §Layer 1 On failure.)
4. Read the last line of `events.jsonl`; let `prev_hash` be its `hash` (or `sha256:0000…0000` if the log is empty).
5. Build the event JSON object: `{id, ts, kind, actor, project, payload, prev_hash}` where `payload` contains the artifact frontmatter and body, and `id` is `EV-<next>` — derived from the tail line already read in step 4, never from project-scoped state (§Deriving the Next Event ID).
6. Compute `hash` per the Hash computation rule above. Append the full event line (with `hash`) to `events.jsonl`.
7. **Regenerate the artifact projection.** Render `projects/<project>/<kind>s/<artifact-id>.md` using the rendering protocol in `core/TYPED-ARTIFACTS.md`. The projection MUST be byte-identical to what a re-render from events would produce.
8. Compute the projection's SHA-256, take the first 12 hex chars, and update `hashes.json` for that path.
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

**Steps.** Read `active_project.md`, `TASK-STATE.yaml`, recent events. Summarize: active project, pending tasks count, blocked tasks, in-progress tasks, recent council outcomes, pending operator review. On an ongoing project, additionally read the last `cycle.close`: if `next_due` < today and no `cycle.open` follows it, lead the status report with **OVERDUE: next cycle was due <date>** — this is the structural replacement for "the operator remembers the weekly sweep."

### `hw log <text>`

Append to backlog without activating a project.

**Steps.**
1. Append `backlog.add` event with `{entry_id, text, ts}`. The agent assigns priority and tags from the text or asks the operator.
2. Re-render `backlog.md`.

### `hw cycle close` / `hw cycle open` (v5.3, ongoing projects only)

Close the current cycle of an ongoing project, or open the next one. See `core/LOCK.md` §Ongoing Projects for when a project qualifies.

**Steps (`hw cycle close`).**
1. Confirm the project's `PROJECT.md` declares `lifecycle: ongoing` and a `cycle.open` exists without a matching close. Otherwise STOP (Layer 1 FAIL).
2. Confirm the cycle's task set is `complete` at Layer 2 (same bar as `hw wrap` step 1, scoped to the cycle's tasks).
3. Compute `next_due = closed_at + cadence_days`. Append `cycle.close` with `{cycle_id, closed_at, summary, next_due}`.
4. Re-render `CYCLES.md` and `active_project.md` (the pointer stays on the project; only `Next due:` changes). The project does **not** archive.
5. Reset the cycle's recurring tasks to `pending` for the next cycle per the schema's `recurring_tasks:` list.

**Steps (`hw cycle open`).**
1. Confirm the prior cycle is closed. Append `cycle.open` with the recorded cadence.
2. Re-render `CYCLES.md`. Announce tasks for the new cycle via `hw next-step`.

### `hw wrap`

Run the project completion protocol. On an `lifecycle: ongoing` project, `hw wrap` is valid only when the recurring need itself has ended (the operator says so explicitly); otherwise use `hw cycle close`. Wrap of an ongoing project with an open cycle is a Layer 1 FAIL.

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

## Single-Writer Rule (v5.3)

**One `events.jsonl` has at most one writer at any moment.** This was always the substrate's silent assumption; two independent field incidents made it law. In both, parallel actors (council members in one; concurrently dispatched session chats in the other) appended to the same log and produced EV-id collisions, multiple chains forking from one tail event, and broken hash chains. The operators' postmortems converged on the same fix, which is now the documented protocol:

- **Parallel actors never append directly.** A parallel actor (council member, delegated subagent, sibling session) writes its output to a **draft file** in its own directory. One serial **convergence writer** — the parent agent, or whoever holds the instance — reads the drafts and appends the resulting events in order.
- **Parallelism across instances, not within one.** If two workstreams genuinely need to write concurrently, they belong in separate harness instances with separate `events.jsonl` files (see `core/LOCK.md` §Programs). The Lock is per-instance; so is the writer.
- **Layer 1 detection.** Duplicate event IDs, or more than one event whose `prev` hash references the same parent, is a `chain_breaks` FAIL in `hw verify` — corruption from a violated writer rule is visible on the next verify, not at the next confusing read.

| Hypothesis | Claim | Falsifier |
|---|---|---|
| H-S5 | Draft-files-plus-one-convergence-writer eliminates the concurrent-append corruption class without a filesystem lock primitive. | A deployment following the protocol still produces EV-id collisions or forked chains, or the draft/convergence ceremony proves heavy enough that operators bypass it and corrupt logs anyway. |

---

## Superseded Artifact Back-Link

When artifact `B` supersedes artifact `A` (i.e., a `<kind>.add` event creates `B` with `reverses: A`), the harness emits a `<kind>.supersede` event automatically (see §Event Kinds). `reverses:` accepts a single ID or a list (v5.3); a list emits one supersede event per reversed artifact — a field run that needed one decision to reverse three priors had to improvise exactly this, so it is now the documented form. The supersede event MUST trigger a re-render of artifact `A`'s projection so that `A`'s frontmatter carries `superseded_by: [B-NNN#hhhhhhhhhhhh]` referencing the superseding artifact's current short-hash.

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

`friction.log` makes friction capture a substrate event, not an operator-instructed prose habit. The failure mode this fixes: the operator says "log friction as you encounter it" at project start; the agent acknowledges; thirty turns later the prompt has been compacted out and friction signal evaporates as an unprompted prose habit. The closing v5.0 lead-magnet run lost real-time friction signal exactly this way. v5.1 makes the harness do the prompting and the recording so the agent's compliance does not depend on remembering a verbal request that is no longer in context.

**Field evidence (v6.0.0):** four `friction.log` entries in 130 events across ten weeks. The mechanism existed, the operator wanted it, and it went unused because filling six fields "felt heavier than the value." The best lessons of the engagement went uncaptured. So the payload is now one line.

**The protocol is one step: append one event.** No artifact file. No projection to hand-write. No classification to get right. Promotion to an anti-pattern or a finding is a **later, optional** act — a separate event, done when the friction turns out to matter, by whoever notices. Getting the note onto the log is the whole obligation.

**Payload schema (v6.0.0).**

| Field | Type | Meaning |
|---|---|---|
| `note` | string | **Required. The only required field.** One line, in whatever words are at hand. "The recitation band rejected three honest paraphrases in a row." |
| `category` | string \| null | Optional. Free text or one of the pre-v6 categories below, if a category is obvious at the moment of writing. Do not stop to decide. |
| `severity` | enum \| null | Optional. `blocking` \| `non-blocking`. |
| `task_id` | string \| null | Optional. The task in flight, if any. |

**Pre-v6 rich form (still accepted).** v5.1-v5.3 chains carry `{type, patch_id, description, surfaced_by, severity, suggested_target}` and keep verifying: `type` ∈ `REGRESSION`, `CONFIRMATION`, `NEW-SCHEMA`, `NEW-CROSS`, `TRAINING-FILL`, `OPERATOR-CONFUSION`; `patch_id` the harness patch this targets or `null`; `description` 1-3 sentences; `surfaced_by` `operator` / `executor:T-NNN` / `council:<role>` / `harness`; `severity` `blocking` / `non-blocking`; `suggested_target` the guessed fix shape. An event is well-formed if it carries `note`, **or** the full rich set; anything else FAILs as a malformed payload. The rich form remains available to anyone who wants it — it is no longer the price of admission.

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

<Slim entries (v6.0.0) render as one line each, newest last — one line in, one line out:>

- `EV-NNNN` — <note> <(category, severity, T-NNN — only the optional fields that are set, in parentheses; omitted entirely when none are)>

<Rich entries (pre-v6) keep their block form:>

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

Long projects span sessions. v5.0/v5.0.1 used informal `SESSION-HANDOFF.md` prose authored by the closing agent — file-canonical, hand-edited, easy to skip. The resuming agent might or might not read it. The failure mode: the closing agent writes a careful 200-word handoff covering open questions and the next-step recommendation; the resuming agent's first instinct is to grep TASK-STATE.yaml and start the next pending task, never opening SESSION-HANDOFF.md. The closing agent's transfer is silently ignored. v5.1 makes handoff a substrate event so the resuming agent has a structural anchor that survives session boundaries by replay, and a frontmatter-flag mechanism for tasks that REQUIRE the handoff to be acknowledged before the first state-changing event.

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

## Scope Completeness

v5.1 sessions could close with §Scope items silently un-actuated and un-classified. The closing agent finished the tasks it picked up, emitted `session.handoff`, and items declared in PROJECT.md §Scope but never tasked simply disappeared from the trail. The cost: an item the operator believed was in flight discovered as un-touched three sessions later, when the project was supposed to be wrapping. The agent had no structural reason to surface it, so it didn't. v5.1.1 adds a structural check at handoff: a `scope.complete` event must record every §Scope item with an explicit terminal state. Items left un-classified fail Layer 1 verification; the session cannot close until every §Scope item has a disposition.

**Payload schema.**

| Field | Type | Meaning |
|---|---|---|
| `scope_items` | list[object] | One entry per item declared in PROJECT.md §Scope (Included + Explicitly Excluded). |
| `scope_items[].id` | string \| null | Task or scope-item ID if one was assigned (e.g., `T-027`). `null` for items declared by name only. |
| `scope_items[].name` | string | Human-readable scope-item name. Required even when `id` is set, for cross-checking against PROJECT.md §Scope. |
| `scope_items[].terminal_state` | enum | One of `complete`, `deferred`, `excluded-after-discovery`, `escalated`. |
| `scope_items[].reason` | string \| null | Reason note. Required for any state other than `complete`; `null` is acceptable for `complete`. |

**Allowed terminal states** are constrained per schema via `capability-gates.yaml` `scope_completeness.allowed_terminal_states`. v5.1.1 ships every schema accepting the full set `[complete, deferred, excluded-after-discovery, escalated]`. Future deploy-shaped schemas may tighten to `complete` only.

| State | Meaning |
|---|---|
| `complete` | The item was actuated to its declared terminal state. |
| `deferred` | In scope, intentionally not actuated this session. The reason captures what gates resumption (operator decision, downstream-task dependency, etc.). |
| `excluded-after-discovery` | Probing the actual surface revealed the item is outside the project's mission. Distinct from §Explicitly Excluded items declared at bootstrap; `excluded-after-discovery` records mid-session learning. |
| `escalated` | The closing actor could not classify the item without operator input. The resuming session's first action is operator reconciliation. |

**Layer 1 enforcement.**

The check runs at `session.handoff`. See `core/VERIFICATION.md` §Layer 1 for the row.

1. Find the most recent `scope.complete` event in `events.jsonl` for this project. If `session.handoff` exists in the chain and no `scope.complete` precedes it, FAIL `scope_completeness_missing`.
2. For each entry in `scope_items`, confirm `terminal_state` is in the schema's allowed set. If not, FAIL `scope_completeness_terminal_state_disallowed`.
3. Cross-check: every PROJECT.md §Scope item must appear (by `id` or `name`) in the `scope_items` array. If a §Scope item is missing from the snapshot, FAIL `scope_completeness_unrepresented_item`.

**Projection.** The most recent `scope.complete` regenerates `projects/<id>/SCOPE-COMPLETE.md` per `templates/artifact-templates/scope-complete.md`. The event itself remains the source of truth; the projection is the human-readable rendering. `hashes.json` tracks the projection.

**Hypothesis (under empirical evaluation in v5.1.1+).** A scope-completeness check at session.handoff catches silent in-scope skips. Falsifier: a declared scope item resolves to no terminal state and verification PASSes.

---

## External State Read-Back

A `task.complete` event records that the agent finished a task. For tasks that mutated state outside `events.jsonl` — a CMS edit, a calendar booking, a remote configuration change, a redirect-list entry — the completion event by itself does not verify the mutation actually landed on the external surface. The failure mode: the agent reports "applied the change" because the API call returned 200; the operator believes the task is done; the underlying CMS silently rejected the payload because of a permissions issue and the change never went live. The completion report says success and the live state says nothing changed. v5.1.1 adds `external_state.read_back` as the structural primitive for capturing the post-mutation re-read. After the mutation, re-fetch the surface and compare; the comparison is what proves the task was actually done.

**Payload schema.**

| Field | Type | Meaning |
|---|---|---|
| `task_id` | string | The task whose mutation this read-back verifies. |
| `artifact_url` | string | The external surface (URL, REST endpoint, file path, `platform://list/redirections`) re-read. |
| `pre_state_ref` | string | Loose reference to the pre-mutation state: `screenshot:<path>`, `hash:<sha256>`, `manual-attestation:<token>`, or `none` if pre-state was not captured. |
| `post_state_ref` | string | Same shape as `pre_state_ref`, but for the post-mutation re-read. |
| `equality_method` | enum | `visual-diff`, `rest-roundtrip`, `manual-attestation`. Documents how equality (or expected divergence) was checked. |
| `divergence_detected` | bool | `true` if the post-state differs from what the mutation should have produced. |
| `divergence_notes` | string \| null | Required when `divergence_detected: true`; describes the divergence. |

**Schema config.** Schemas opt in via `capability-gates.yaml` `external_state_readback.required_for`. The list contains task patterns or task kinds; a task matching any pattern requires a paired `external_state.read_back` event after `task.complete`. v5.1.1 enables this only for marketing-campaign; other schemas adopt as their delivery shape requires.

For platforms that do not surface state for re-read, the schema declares a `fallback_equality_method: manual-attestation` and the agent records the operator's attestation as the `post_state_ref`.

**Layer 1 enforcement.** See `core/VERIFICATION.md` §Layer 1.

1. For each `task.complete` whose task matches a `required_for` pattern, find a paired `external_state.read_back` event with the same `task_id`, later than the `task.complete`, within 5 events. If absent, FAIL `external_state_readback_missing`.
2. If `divergence_detected: true` on the read-back, emit a Layer 1 WARNING (not FAIL) and require a follow-up `friction.log` event referencing the divergence.

**Hypothesis (under empirical evaluation in v5.1.1+).** `external_state.read_back` makes external mutation verifiable per critical-risk task. Falsifier: a critical-risk `task.complete` ships without a paired read_back event and Layer 1 PASSes.

---

## Bootstrap Inventory Sweep

v5.1 §Scope was operator-declared and never cross-checked against the actual project surface. The failure mode: the operator names ten pages they want updated; one slug is wrong (renamed three months ago), one page doesn't exist (was archived), one was a draft (never published); these don't surface until task T-007 fails to find its target and the agent has to re-bootstrap PROJECT.md mid-project. The wrong slug bit later, not earlier, when the cost of fixing it had compounded. v5.1.1 inserts a probe between `bootstrap_questions` and §Scope locking: the executor probes the project's ground truth (CMS pages, source filesystem, git tree, etc.) and emits `bootstrap.inventory_diff`. The operator reconciles the diff before §Scope is written into PROJECT.md, so wrong slugs and missing pages surface at minute one, not week three.

**Payload schema (`bootstrap.inventory_diff`).**

| Field | Type | Meaning |
|---|---|---|
| `schema` | string | Schema ID for the project being bootstrapped. |
| `probe_method` | string | The probe used (e.g., `wp-rest-pages-list`, `git-ls-files`, `filesystem-listing`). Documented per schema in `bootstrap-probe.md`. |
| `declared` | list[string] | Items declared via `bootstrap_questions` answers (slugs, paths, control IDs). |
| `found` | list[string] | Items the probe surfaced from ground truth. |
| `missing_from_declared` | list[string] | `found` items not present in `declared`. |
| `missing_from_found` | list[string] | `declared` items not present in `found`. |
| `operator_reconciliation` | object \| null | Per-item disposition (confirm declared, expand declared, mark out-of-scope). `null` until operator reconciles; a populated value gates `bootstrap.scope_locked`. |

**Ceremony close.** After operator reconciliation, the executor emits `bootstrap.scope_locked` with the final scope-item list. §Scope is then written into PROJECT.md from this event's payload.

**Skip path.** Schemas whose probe is stubbed (or whose project surface cannot be probed automatically) emit `bootstrap.probe_skipped` with a reason. The skip is recorded in the chain so verification can distinguish "probe ran, no diff" from "probe was never attempted."

**Per-schema probe.** Each schema documents its probe method in `schemas/projects/<schema>/bootstrap-probe.md`. The agent reads the schema's probe doc at bootstrap and executes it; the doc declares the API call, filesystem walk, or operator-attest fallback that produces the `found` list.

**Layer 1 enforcement.** See `core/VERIFICATION.md` §Layer 1.

A project's chain must contain either:

1. `bootstrap.inventory_diff` followed by `bootstrap.scope_locked` whose payload's `operator_reconciliation` (or the prior diff event's `operator_reconciliation`) is populated; OR
2. `bootstrap.probe_skipped` with a reason.

If neither is present after `project.activate`, FAIL `bootstrap_probe_missing`.

**Hypothesis (under empirical evaluation in v5.1.1+).** `bootstrap.inventory_sweep` surfaces declared-vs-actual mismatches before §Scope locks. Falsifier: a wrong slug or missing page in PROJECT.md §Scope makes it past bootstrap and bites mid-task.

---

## Operator Soul Anchor

The failure mode `operator_soul_anchor` addresses: the operator declares operating identity (quality bar, refused workarounds, voice/posture, when-in-doubt defaults) in conversation at project start; the agent acknowledges; the prompt fills with project content; the identity declaration evaporates from context. Three sessions in, the agent is shipping work that "would normally be done in a real run" or "we can table the regression test for later" — patterns the operator explicitly refused. The operator catches it on review and the cycle repeats.

The substrate fix: a file-canonical operator-identity anchor (`soul.md` at workspace root, or operator-declared path) is read at bootstrap and recorded as an `operator_soul_anchor` event. Every council fire that includes the `soul_consistency_watcher` member (see `core/VERIFICATION.md` §Council Role Library) reads the anchor's content from the recorded event hash; the anchor is structural, not a verbal request.

**Payload schema.**

| Field | Type | Meaning |
|---|---|---|
| `soul_path` | string | Path to the operator's filled-in soul.md (typically `soul.md` at workspace root, but the operator may declare another path in `OR-001.soul_anchor_path`). |
| `soul_hash` | string | SHA-256 of the file's bytes at bootstrap, full hex. Used by `soul_consistency_watcher` to detect drift; if the file changes mid-project, a new `operator_soul_anchor` event must be appended. |
| `version` | string | `1.0.0` for v5.2.0. Reserved for future schema-extensibility of soul.md content. |
| `fired_at` | string | ISO 8601 UTC timestamp. |

**When fired.** At bootstrap, after `project.activate` and before any task can transition `pending → in_progress`, if `OR-001.soul_anchor_path` is declared (or if `soul.md` exists at workspace root and the schema declares `soul_anchor_required: true`).

**Skipped path.** If no soul.md exists and the schema does not require one, the harness emits no `operator_soul_anchor` event. Council fires that include `soul_consistency_watcher` skip the member with a `member_skipped: no_soul_anchor` note in the projection. The remaining members proceed normally.

**Re-anchoring on file change.** If `soul.md` changes mid-project (operator updates the quality bar, adds a refused anti-pattern), the operator emits a new `operator_soul_anchor` event with the new hash. The supersede chain captures the change; subsequent `soul_consistency_watcher` fires read the latest anchor.

**Brand isolation.** Substrate ships `SOUL.template.md` (brand-clean structural stub) and `SOUL.example.md` (one filled-in example, with operator-specific names genericized). Operators copy the template, fill in their own content, and save as `soul.md` (operator-side, never committed to the harness substrate).

**Hypothesis (under empirical evaluation in v5.2.0+).** A structural operator-identity anchor produces qualitatively different agent behavior than rules-based prose alone. Falsifier: `soul_consistency_watcher` never fires across 5+ real runs (the anchor is not load-bearing) OR fires constantly on every task (the anchor is poorly written and dilutes the Tier 1 boundary).

---

## Toolchain Anchor (v5.2.1)

The failure mode `toolchain.anchor` addresses: every hash the harness depends on — event hashes, projection hashes, recitation overlap scores — requires *running code*. An agent cannot compute SHA-256 or stemmed Jaccard by generating tokens; it must write and execute a script. Left unspecified, every session improvises a fresh implementation: ad-hoc scripts with subtle serialization divergence (the exact divergence §Canonical Serialization warns about), or — the worst case — fabricated hashes that look plausible and were never computed at all. The substrate's entire integrity story rests on byte-identical serialization, and per-session reimplementation is exactly where it quietly breaks. The harness deliberately ships near-zero code so operators can review what they deploy; the cost of that choice is that the code gets written anyway, at runtime, unreviewed, N times.

The substrate fix: generate (or adopt) the toolchain **once**, pin it, and verify it ever after.

**Protocol.**

1. **First run.** The agent assembles the minimal toolchain for hash-computing operations: an event appender, a projection regenerator, a recitation scorer, and the verifier. Where a reference implementation ships (`tools/hw-verify.py`), adopt it (`source: shipped`). Where none ships, generate it from the protocol specs in this file and write it to `.hyperworker/tools/` (`source: generated`).
2. **Pin.** Compute the SHA-256 of each tool file's bytes. Emit `toolchain.anchor` with `{tools: [{name, path, sha256}], source, spec_version, fired_at}`.
3. **Every subsequent session.** Before the first hash-computing operation, re-hash each pinned tool and compare against the most recent `toolchain.anchor` event. Match → proceed, using the pinned tools (never a fresh reimplementation). Mismatch → Layer 1 FAIL `toolchain_drift`; do not use the drifted tool; the operator inspects the diff and either restores the pinned version or deliberately re-anchors.
4. **Deliberate change.** Improving a tool is legitimate; doing it silently is not. The operator (or agent, with operator visibility) emits a new `toolchain.anchor` after the change. The anchor chain records every toolchain the workspace has ever trusted.

**Review surface.** This pattern preserves the no-shipped-code reviewability goal in a stronger form: instead of "no code exists" (false — it exists per-session, unreviewed), the contract becomes "exactly one copy of the code exists, it is small, its hash is in the log, and it never changes without an event." An operator audits the toolchain once per anchor, not never.

**Hypothesis (under empirical evaluation in v5.2.1+).** Pinning generated tools eliminates per-session serialization divergence and fabricated-hash failures. Falsifier: a workspace with an anchored toolchain still produces inter-session hash divergence, OR agents observed bypassing the anchored tools to hand-roll hashing anyway.

---

## Checked Claims (v5.3)

The chain proves events were not tampered with; it never proved the events were true. The motivating field incident: an infrastructure-recovery engagement's own postmortem states it as the thesis of the whole patch — *"The hash chain did its job. It proved nothing was tampered with. It could not prove anything was true."* Three independently-authored records on that engagement — an agent's completion report, a human-kept ledger, and a harness projection — all asserted the same two files were `posted`. None of the three were true. `hw verify` passed for the full duration because integrity and truth are different properties, and nothing in the substrate checked the second one.

The fix is deliberately narrow: an optional `claim:` block on payloads that assert world-state, carrying a machine-checkable predicate plus the result observed when the event was authored. `hw verify` gains a second, independent mode — replay (`--claims`) — that re-runs the same predicates against the world as it stands now and reports claim-level truth, kept structurally separate from chain-integrity results. A workspace can PASS integrity and FAIL claim replay in the same breath; that is the primitive working as designed, not a contradiction.

**Where `claim:` is valid.** The payload of `task.complete`, `finding.add` (and, by schema opt-in, the other typed-artifact `.add` kinds), `external_state.read_back`, and — at per-item granularity, since the event is already itemized — each entry of `scope.complete`'s `scope_items[]`. A `claim:` block appearing on any other event kind is not read by Layer 1 or by `--claims` replay.

**Payload schema (`claim:` block).**

| Field | Type | Meaning |
|---|---|---|
| `predicate` | object | Exactly one key, one of the five kinds below. Zero keys or more than one is a structural failure. |
| `checked_at` | string | ISO 8601 UTC — when the authoring agent evaluated the predicate, not when it is replayed. |
| `passed` | bool | The result recorded at `checked_at`. Fixed at write time; a later disagreement is a replay finding, never a correction to this field — the substrate is append-only even here. |

**Predicate kinds.**

| Kind | Shape | Evaluates to true when |
|---|---|---|
| `file_exists` | `<path>` (string) | A file exists at `<path>`. |
| `file_absent` | `<path>` (string) | No file exists at `<path>`. |
| `file_sha256` | `{path, hash}` | The file at `path` has SHA-256 (full hex) equal to `hash`. |
| `cmd_exit` | `{cmd, expect_substring, expect_code}` | Running `cmd` exits with `expect_code` (default `0`) and, if `expect_substring` is set, combined stdout+stderr contains it. |
| `url_status` | `{url, expect_code}` | An HTTP(S) request to `url` returns status `expect_code`. |

All `<path>` values are relative to the workspace root (§File Layout), never absolute — a claim recorded on one operator's machine must still replay on a fresh checkout on a different one.

**`cmd_exit` and the shell-capability gate.** `cmd_exit` is the one predicate that executes arbitrary code, so it does not get its own permission model — it inherits the substrate's existing one. A workspace's active schema declares whether shell execution is available at all via `capability-gates.yaml` (`task_capabilities.*.required_tools` containing `shell_exec`, and its absence from `not_required`; see e.g. `schemas/projects/report-synthesis/capability-gates.yaml`, which excludes it entirely). `cmd_exit` predicates are only executed — at authoring time or at replay — in a workspace whose schema declares `shell_exec` available. `hw verify --claims` additionally requires the operator to pass `--allow-cmd`: two independent gates (schema capability + explicit operator flag) must both be open, since a replay pass is exactly the kind of unattended, later-in-time execution that shell predicates make riskiest. Absent either gate, `cmd_exit` claims report `skipped`, not `fail` — an unevaluated predicate is not a broken one.

**Never required by default.** A `claim:` block is optional cargo on every payload above unless a schema opts a kind in. Opt-in is per-schema, in `verification.yaml`:

```yaml
# schemas/projects/<name>/verification.yaml
checked_claims:
  required_for:
    - finding.add
    - task.complete:critical      # risk_level-scoped, task.complete only
    - external_state.read_back
    - scope.complete               # every scope_items[] entry must carry a passing claim
```

A bare event kind requires every event of that kind to carry a `claim:` block with a well-formed predicate and `passed: true`. Appending `:<risk_level>` (valid only on `task.complete`) scopes the requirement to tasks authored at that risk level, read from the task's `task.create` frontmatter — mirroring how `external_state_readback.required_for` patterns already scope by risk (§External State Read-Back). No `verification.yaml`, or no `checked_claims` key in it, means the requirement is off; ceremony stays proportional to what the schema author actually asked for.

**Layer 1 enforcement.** See `core/VERIFICATION.md` §Layer 1. Two independent checks: (1) any `claim:` block present anywhere in the chain, required or not, must be structurally well-formed (single known predicate kind, `checked_at`, `passed` present) — malformed claims fail `checked_claims_malformed` regardless of schema config; (2) for event kinds a schema marks `required_for`, a matching event without a well-formed, `passed: true` claim fails `checked_claims_missing` (block absent or malformed) or `checked_claims_predicate_failed` (block present, well-formed, `passed: false`). Both are structural failures — a `task.complete` claiming a file was posted, checked, and found absent should never reach `complete` state quietly.

**Replay mode — `hw verify --claims`.** A second, opt-in mode: instead of (or alongside) integrity replay, walk every recorded `claim:` block in the chain and re-evaluate its `predicate` against the world *now*. This is a fundamentally different question than integrity replay answers — "is the event log internally consistent" versus "is what the log asserts still (or ever) true" — so the two run and report independently; a `--claims` FAIL never flips the integrity `result` field and vice versa. Report format and CLI flags are specified in `core/VERIFICATION.md` §Claim Replay.

| Hypothesis | Claim | Falsifier |
|---|---|---|
| H-S4 | Recording a machine-checkable predicate alongside every world-state claim, and replaying it later, catches the class of failure where chain integrity holds but the asserted world-state was never true (or stopped being true). | Predicates rot faster than they're useful — paths move, commands drift, so replay failures are overwhelmingly false alarms operators learn to ignore — or agents satisfy the letter of the check by asserting trivial/tautological predicates (e.g. `file_exists` on a file they just touched, not the actual deliverable) while the substantive claim stays unchecked. |

---

## Evidence Capture (v6.0.0)

**Field evidence:** across ten weeks, the raw outputs and error codes that decisions actually rested on survived only where a human hand-copied them into a side ledger. Everything else died with the session that produced it.

An agent runs a command, reads 40 lines of output, concludes something, and writes the conclusion. The output is gone at the next compaction. Three sessions later the conclusion is load-bearing and unfalsifiable: nobody can see what it was based on, so nobody can tell that the command was run against the wrong host.

`evidence.capture` keeps the bytes.

**Payload schema.**

| Field | Type | Meaning |
|---|---|---|
| `id` | string | `ED-NNN`, unique across the whole log (like `EV-` ids, not per project). |
| `producing_command` | string | The exact command, request, or action that produced this output. |
| `captured_at` | string | ISO 8601 UTC. |
| `content` | string | The output itself, inline. **Sanitized** — no credentials, tokens, keys, or customer data. |
| `content_path` | string | Alternative to `content` for large or binary output: a workspace-relative path. |
| `content_sha256` | string | Required with `content_path`. Full hex of the file's bytes, so the capture still pins what was captured. |
| `summary` | string | One line: what this output shows. |

Exactly one of `content` or `content_path` (+ `content_sha256`). Inline is the default; the path form exists so a 4 MB log does not enter the hash chain. Sanitize before capture — the log is append-only, so a leaked secret cannot be deleted, only rotated.

**Who cites it.** `test_ref` on an excluded hypothesis (§Exclusion Discipline), the `evidence` field of a finding, a completion report. `ED-014` is the citation form; it needs no hash, because the event log's own chain already fixes the content.

**Projection.** `projects/<id>/evidence/ED-NNN.md`, one file per capture, from `templates/artifact-templates/evidence-capture.md`. Tracked in `hashes.json` like any projection.

**Layer 1 (check 20).** Well-formedness and `ED`-id uniqueness: `evidence_id_malformed`, `duplicate_evidence_id`, `evidence_capture_no_content` (neither form present), `evidence_capture_content_ambiguous` (both forms — one authority per capture), `evidence_capture_path_without_hash`. See `core/VERIFICATION.md` §Layer 1 check 20.

| Hypothesis | Claim | Falsifier |
|---|---|---|
| H-S7 | Making raw output a substrate event, cheap enough to fire mid-work, keeps load-bearing evidence alive past the session that produced it — and gives exclusions something to cite. | Captures are fired for trivia and the important output still goes uncaptured, or the inline-content rule pushes agents to summarize at capture time, which is exactly the loss the primitive exists to prevent. |

---

## Exclusion Discipline (v6.0.0)

**Field evidence:** AP-008 — the true root cause was crossed off the hypothesis list on the strength of a well-argued static read, and ~19 further attempts were burned before anyone went back to it.

Ruling a hypothesis out is the single most expensive thing an agent does, because everything after it is searched somewhere else. A static read — "I read the code path and it cannot be this" — is an argument, not a test. It was wrong once at a cost of nineteen attempts, and nothing in the substrate could tell the difference between it and a measurement.

**The rule.** One line: *nothing is excluded without a dynamic test.*

| Status | Means | Requires |
|---|---|---|
| `open` | Not investigated yet. | Nothing. Default. |
| `suspect` | Argued for or against, including by careful static reading. Still live. | Nothing. This is where a static read lands. |
| `excluded` | Ruled out. Stop searching here. | `test_ref` naming a **dynamic** test that exercised the actual code path. |

`status` and `test_ref` are optional fields on a `finding.add` payload (`schemas/artifacts/finding.yaml`), used when a finding is being carried as a hypothesis. `test_ref` is one of:

- an `evidence.capture` id — `ED-014` — the raw output of the command that exercised the path (§Evidence Capture); or
- a checked-claim predicate: the same event carries a `claim:` block whose predicate was actually run (§Checked Claims).

A prose justification is not a `test_ref`. If you did not run something, the hypothesis is `suspect`.

**Layer 1 (check 19).** `excluded` with no `test_ref` FAILs `excluded_without_test_ref`. A `test_ref` naming an `ED-NNN` that is not in the chain FAILs `excluded_test_ref_unresolved` — a citation to a capture nobody made is the same failure wearing a test's clothes. A `status` outside the enum FAILs `invalid_hypothesis_status`. See `core/VERIFICATION.md` §Layer 1 check 19.

**Projection.** `projects/<id>/ELIMINATION.md` (`templates/ELIMINATION.md`): a one-line frontier at the top, then the matrix. In the field this document was handed to every new agent *first*, and it was what stopped each fresh context from restarting the same generic checklist.

| Hypothesis | Claim | Falsifier |
|---|---|---|
| H-S6 | Requiring a dynamic `test_ref` to exclude a hypothesis prevents the class of failure where a well-argued static read removes the true cause from the search space. | Agents satisfy the check with a nominal capture that did not exercise the path (a test in name only), or the requirement is heavy enough that they leave everything `suspect` and the matrix stops discriminating. |

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
| Operator identity | `operator_soul_anchor` event; read by Verification's `soul_consistency_watcher` council member at every council fire that includes the role. |
| Checked claims (v5.3) | `claim:` block on `task.complete`, `finding.add`, `external_state.read_back`, `scope.complete` `scope_items[]`; Layer 1 structural + schema-required checks; `hw verify --claims` replay mode. See `core/VERIFICATION.md` §Claim Replay. |
