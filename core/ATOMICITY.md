# Mechanism: Atomicity — One Task, Hermetic Working Set, Capability-Gated

> An atomic task fits one session, declares its upstream working set, and declares its tool capability requirement. Three predicates; all three required. Branch/fold preserves exploratory subwork in events while keeping the parent context clean. Capability gates prevent the v4.1.1 failure mode where subagents were delegated work without the tools to do it.

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
| `read_only_pass` | Optional (v6.0.0). `true` means: read, measure, capture evidence, report — mutate nothing this pass. Unlike the other frontmatter fields it may be added **after** the task is issued, and the executor picks it up by re-reading `task.md` immediately before its first state-changing action (`templates/executor-prompt.md`). From EV-0042, where exactly such a gate was added to an issued task and never reached the executor before it acted. See `core/SUBSTRATE.md` §Read-Only Pass. |

---

## Hermetic Working Set

The agent executing this task reads, in addition to `task.md`:

1. `00-REFERENCE-rules.md` for the active project (Tier 1 rules cannot be hidden by hermeticism).
2. The project's compressed reference content (`*.compressed.md`; see `core/TYPED-ARTIFACTS.md` §Compression).
3. Each artifact in `consumes:` — read-only, by exact ID and hash.
4. `templates/executor-prompt.md`.

Anything outside that list is **not** mounted. The failure mode hermeticism prevents: an agent in mid-task spots a related artifact ("oh, F-019 looks relevant"), reads it, and now its decision is influenced by a finding that was never declared as upstream input. Downstream tasks cannot tell whether the agent used F-019; the recitation projection does not show it; the dependency graph cannot reason about it.

If another artifact is needed, STOP and emit a `task.status` to `blocked` with a `reason: missing_consumes <artifact>`. The planner adds the artifact to `consumes:` and unblocks. One pause, one explicit edge added to the graph, full recitation visibility.

This is the v5.0 form of "Do NOT Touch": positive scope by enumeration of `consumes:`, not negative scope by enumeration of forbidden files.

---

## Delivery Modes

| Mode | Who writes | When |
|---|---|---|
| `prescribed` | Planner authors content during planning; executor pastes it exactly. | Regulated, brand-critical, or legally sensitive content. |
| `constrained` | Executor generates content within declared boundaries. | Most creative or technical work. |
| `bounded-iteration` | Executor produces N candidates against a preview surface; operator selects or redirects; capped by max passes. | Visual / design / copy exploration where first-pass fidelity is impossible. |
| `ab-variant` | Executor produces N differentiated variants in a single pass; each is its own artifact with its own hash. | Any case where multiple intentionally-differentiated outputs are the right answer (copy variants, design alternatives, prompt phrasings, deployment-strategy options). |

`bounded-iteration` requires three additional fields:

```yaml
preview_surface: "https://staging.example.com/banner-preview"
version_naming: "banner-v{N}.png"
convergence_criterion: "operator approves OR three passes elapsed"
max_passes: 3
```

STOP on convergence or max-passes, whichever comes first. Iteration is bounded.

`ab-variant` requires two additional fields:

```yaml
ab_variant_count: 3                # integer, range 2-5; default 3
ab_variant_axis: "primary CTA framing"  # what dimension the variants differ on
```

Produce exactly `ab_variant_count` artifacts, each its own projection with its own hash. Each artifact's body identifies which variant it is (e.g., a `variant: A` frontmatter field or a `Variant A — <axis-position>` heading). Layer 1 citation rules apply per variant: the recitation projection cites the source artifacts each variant consumed; the schema validation runs on each variant independently. The completion report enumerates all N artifact IDs produced.

`ab-variant` is for **intentional variation**, not **iteration toward a single winner**. Tasks that produce multiple drafts and then pick one are `bounded-iteration`. Tasks that produce multiple drafts that ship together (campaign A/B test, design alternatives presented to operator, deployment options for staged rollback) are `ab-variant`.

An optional council role, `variant-comparison-watcher`, may be added to a schema's council when a task declares `ab-variant`. The role verifies that the variants meaningfully differ on the declared `ab_variant_axis` rather than being trivially paraphrased. See `core/VERIFICATION.md` §Council Role Library.

---

## Task State Projection (`TASK-STATE.yaml`)

`TASK-STATE.yaml` is a projection. The render protocol:

1. Group `task.create` events by `phase`. For each phase, list tasks in ID order.
2. For each task, compute current status as the most recent `task.status` event's `to` value (or `pending` if no status events). If the latest event is `task.complete`, status is `complete`.
3. Write `consumes` and `depends_on` from frontmatter (which the `task.create` payload captured).
4. Write `read_only_pass: true` for any task whose `task.md` currently declares it (v6.0.0). This one field is re-read from `task.md` at render time rather than taken from the `task.create` payload — the gate exists precisely to be addable after the task was issued. Omit the key when false.

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
        read_only_pass: true          # v6.0.0, optional; present only when task.md declares it
        completed_at: "2026-04-26T11:14:09Z"
  2:
    name: "Nurture"
    checkpoint: "PAUSE — operator approves Phase 1 outputs"
    tasks:
      - id: T-002
        ...
```

The projection is byte-deterministic from events: same event prefix → same YAML. Operators who hand-edit `TASK-STATE.yaml` lose their edits on next regeneration.

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

Legal transitions (emit `hw write <task-id> --status <state>` to record):

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

When a task needs exploratory subwork — drafting alternatives, investigating an unknown — emit `hw branch <task-id> <branch-name>`. See `core/SUBSTRATE.md` §`hw branch` for the protocol.

The failure mode branch/fold prevents: exploratory work pollutes the parent task's context. The parent agent has now "remembered" three abandoned drafts plus the chosen one; downstream decisions reference scaffolding that no one ever shipped. The parent's prompt window fills with sub-trajectory; later tasks inherit the noise.

**Inside a branch.** The branch is a fresh atomic task. Its `task.md` declares its own `consumes` (often a subset of the parent's), its own `acceptance_criteria`. Its events are tagged with the branch ID and aggregated under `branch.event` envelopes.

**Folding.** `hw fold <task-id>/<branch> --result "<text>"` collapses the branch:

1. The branch's full event sub-trajectory remains in `events.jsonl` under `branch.event` payloads.
2. A 1–3 sentence `result.md` projection is written to `branches/<branch>/result.md`.
3. The parent's read-set on next turn includes only `result.md`, not the branch trajectory.

The parent's context window does not have the choice of "remember the whole branch." The branch trajectory is in the log; the projection the parent reads is the result. Context discipline is enforced by the projection rendering protocol, not by the agent's restraint.

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

These capability slugs are also the slugs a shared tools catalog declares as `capabilities_provided` — before building a tool to satisfy one, check the catalog, and verify anything you fetch by hash and check predicate (`core/TOOLS.md`; the harness is fully functional with no catalog reachable).

**Delegation gate.** When the parent agent intends to delegate this task to a subagent, the harness composes the subagent's tool schema as `agent.provides ∩ task.required_tools`.

- If `task.required_tools ⊆ agent.provides`, the subagent receives exactly the required tools. Delegate.
- Otherwise, the harness **refuses to delegate** and emits `capability.gap` with `{task_id, agent_id, missing_tools}`. It writes `projects/<id>/tasks/<task-id>/capability_gap.md` listing the missing tools and the available alternatives.

**Fallback paths.** When a gap is reported, the operator chooses:

1. Run in-line on the parent agent (which has full tools).
2. Add the missing capability to an existing agent profile.
3. Spawn a different agent with the required tools.

The agent never silently degrades or attempts a tool not in its schema. The schema *is* the boundary; "did the agent comply" is not a question worth asking.

### Delegation Policy (v5.1, optional OR field)

When `OR-001.delegation_policy` is declared, the harness consults it before dispatch:

| Field | Effect |
|---|---|
| `mode` | `step-by-step` — pause for confirmation between substantive moves; `run-to-completion` — proceed without pausing except on `pause_on` triggers; `hybrid` — confirm at phase boundaries only. |
| `execution_mode` | `interactive` (default) — pause at every standard pause point as in v5.1; `agent` (v5.2.0) — autonomous up to safety floors; `observer` (reserved, not yet implemented; declaring it is accepted but produces a Layer 1 WARNING on dispatch). See §Execution Mode below. |
| `subagent_use` | `never` — execute every task on the parent agent; `when-helpful` — dispatch when the task fits a subagent profile cleanly; `aggressive` — dispatch any task whose `required_tools` are a clean subset of an available subagent. |
| `pause_on` | List of triggers that force a pause regardless of `mode`. The harness emits a `task.status → blocked` with `reason: pause_on <trigger>` and waits for `resume_authority` to act. |
| `resume_authority` | `operator-only` — only an operator-actor `task.status` event resumes; `agent-judgment` — the agent may resume itself after a brief pause; `both` — either suffices. |

**Soft enforcement.** v5.1 ships `delegation_policy` as soft enforcement: the agent reads the field at dispatch time and complies. The harness does not block dispatch on violation. If the field is set and operator interventions still occur at the same rate as without it, the falsifier is met (see spec H-F5) and v5.1.x revisits. Hard enforcement (e.g., refusing to dispatch a subagent when `subagent_use: never`) is deferred to v5.2 if needed.

The active model profile may declare default delegation behaviors for fields the operator did not set; OR overrides profile defaults.

### Execution Mode (v5.2.0, `delegation_policy.execution_mode`)

The failure mode `execution_mode` addresses: agentic-coder workflows (Copilot-style billable runs, large-context Claude sessions) burn cycles paused at every `task.complete` boundary waiting for an operator that has authorized the work. Each pause is a 5-15 minute context-switch for the operator and a credit-clock continuing to tick. Across a 9-task project, the cumulative pause cost can exceed the substantive-work cost. `execution_mode` lets the operator declare, once at bootstrap, "take this autonomous unless you hit a safety floor."

| Mode | Behavior |
|---|---|
| `interactive` (default) | Current v5.1 behavior. Pause at phase boundaries, council failures, Layer 1 retries-exhausted, every `task.complete`. The operator sees and approves each transition. Default for OR-001 when `execution_mode` is omitted. |
| `agent` (v5.2.0) | Proceed autonomously up to the safety floors below. Phase boundaries: announce, continue. Council failures: attempt council remediation up to 3 cycles before escalating. Soft warnings: logged to events, not surfaced as pauses. Operator sees an async stream of progress events; intervention at any time still takes precedence (see Safety Floors). |
| `observer` (reserved) | Not implemented in v5.2.0. Declaring it is accepted but Layer 1 emits a WARNING and the harness behaves as `interactive`. Reserved for future "audit-only, no state-changing events" mode. |

**Safety floors (always pause regardless of `execution_mode`).** `agent` mode does not skip these. The harness emits `task.status → blocked` with the appropriate `reason:` and waits for operator action.

| Safety floor | Trigger | Reason code |
|---|---|---|
| Critical-risk task completion | Any `task.complete` whose task has `risk_level: critical`. The substrate cannot reverse an irreversible external mutation; the operator gates it. | `safety_floor_critical_completion` |
| Smoke-run language | A council member's `finding` text contains a smoke-run marker phrase (configurable per schema; default set: "would normally", "in a real run", "this is a placeholder", "demonstrating the structure"). The agent has reported simulated work as actual work. | `safety_floor_smoke_run` |
| Layer 1 retry threshold exhausted | Same Layer 1 check has failed (active model profile `retry_budget`) consecutive times on the same `target_id` within one task. Burning cycles indefinitely is not autonomous; it is stuck. | `safety_floor_layer1_exhausted` |
| Voice / soul anchor breach | `soul_consistency_watcher` council member returns FAIL on a `task.complete` (see core/VERIFICATION.md §Council Role Library). Agent has drifted from operator-declared identity; structural intervention required. | `safety_floor_soul_breach` |
| Operator mid-flow directive | An `actor: operator` event of any kind lands in the log. The directive is captured immediately as a Decision (per HARNESS.md §Operator mid-flow directives), and the current task pauses to incorporate it before the next state-changing event. | `safety_floor_operator_directive` |

The safety floors are intentionally non-overridable. An operator who sets `execution_mode: agent` AND wants to disable a safety floor must amend the substrate, not the OR-001 field — the floors are the cost of autonomous operation, not negotiable parameters.

**Soft enforcement, like sibling fields.** v5.2.0 ships `execution_mode` as soft enforcement: the agent reads the field, treats safety floors as hard, and treats batched events as informational. The harness does not block dispatch on violation. If `agent` is set and operator interventions still occur at every standard pause point, the falsifier is met (see hypothesis H-V52-2 in CHANGELOG) and v5.2.x revisits.

### Model Selection Policy (v5.1, optional OR field)

When `OR-001.model_selection_policy` is declared, the harness picks a model at every subagent dispatch (per `delegation_policy.subagent_use`) and at every council-member instantiation, by consulting profile rankings:

| Field | Effect |
|---|---|
| `prefer` | `cheapest-capable` / `fastest-capable` / `most-capable` resolve through the per-profile rankings (`relative_cost`, `relative_capability`, `relative_speed` in `templates/models/<profile>.yaml`); `manual-only` prompts the operator. |
| `fallback_trigger` | The substrate event that forces a re-dispatch. `layer1-failure-after-N` triggers when the same Layer 1 check fails N times on the same target (N from active model profile `retry_budget`); `layer2-failure` on any `verify.layer2.fail`; `council-non-convergence` on `council.escalated`; `never` disables fallback. |
| `fallback_target` | Explicit `profile_id` to fall back to. May be a more-capable model than `prefer` would normally select; the operator declares the explicit target so fallback is deterministic. |
| `per_task_overrides` | List of `{task_kind, prefer}` pairs. If the dispatched task's `kind` matches, the override's `prefer` replaces the top-level `prefer` for this dispatch. |

Resolution algorithm and override semantics are documented in `templates/models/README.md` §v5.1 — model_selection_policy resolution. Operators with non-default rosters override the per-profile rankings in `templates/models/_ranking.yaml`.

**Soft enforcement.** v5.1 records the chosen profile in the dispatch event but does not block if `prefer: cheapest-capable` is set and an agent self-routes to a more-capable model anyway. If observed rates indicate the policy is ignored, the falsifier in spec H-F8 is met.

**Pairing with delegation_policy.** Together, `delegation_policy` (whether to delegate, when to pause) and `model_selection_policy` (which model to use when delegating) capture engagement and cost preferences in one place at bootstrap, propagating across sessions without per-task re-prompting.

---

## Ratchet

A completed task that introduces a regression in a previously-completed task is not actually complete. The failure mode this prevents: a "nice-to-have" tweak in T-009 supersedes DEC-003, which T-005 cited at hash a3f9. T-005's recitation is now stale, and T-005's output (already shipped) was built on a now-revised premise. Without the ratchet, this drifts silently.

**Detection.** When a `task.complete` event is appended, the harness:

1. Re-runs Layer 1 citation checks across **all complete-status tasks** for the project. Any citation that was valid and is now stale is flagged.
2. If any prior task's `consumes` list contains a citation whose hash changed because of the new task's outputs, the prior task is moved back to `blocked` via a `task.status` event.
3. The blocking event records `reason: ratchet <new-task> superseded <artifact>`.

The state engine drives this; the agent does not need to remember to check. A regression structurally cannot remain hidden because Layer 1 runs on every event and citation freshness is a calculation, not a judgment.

---

## Resume Without Session State

v4.1.1 maintained `SESSION-STATE.md` with per-step writes to support mid-task resume. v5.0 removes this. Resume is replay-based:

1. Read `events.jsonl` for events with `actor` matching the resuming agent or task. Under `profile: single-executor` (`core/SUBSTRATE.md` §Execution Profile) an event carrying no `actor` is treated as `actor: executor` for this selection, so a chain that omits the field resumes exactly as one that writes `executor` on every line. The same default governs `hw fold`'s branch-event capture.
2. Reconstruct context from the consumed-inputs projection (already up to date), the task instructions, and the most recent in-progress markers in events.
3. If a task was mid-step when interrupted, the projected state shows status `in_progress`; re-run from the last completed step inferred from events.

Step-level granularity is now derivable from the event log instead of written redundantly. Tasks that genuinely need finer granularity should be decomposed further, not given a parallel state file.

---

## Boundaries

| Positive | Enumerated by `consumes:`. Read exactly these artifacts plus the rules file plus the task instructions. |
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
