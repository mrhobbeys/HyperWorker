# Mechanism: Verification — Pyramid

> Most failures should be caught at the cheap-fast layer. Mid-cost behavioral checks and high-cost judgmental review are reserved for what they are actually good at. Stacking eight components against every task — v4.1.1's posture — buries cheap structural failures under expensive review and costs operator attention every time. Cross-family or context-asymmetric verification produces less correlated errors than single-context same-family review.

This mechanism replaces v4.1.1's eight-component Verification mechanism. The pyramid is the load-bearing change: every check is now classified by cost and routed by risk, instead of stacked as eight components every task runs.

---

## Hypotheses

| ID | Claim | Falsifier |
|---|---|---|
| H-V1 | Most failures are caught at Layer 1 (cheap structural). Layer 2 (mid behavioral) and Layer 3 (judgmental) are reserved for their actual leverage. | Layer 3 (council/operator) consistently catches what Layer 1 should have. |
| H-V2 | Context-asymmetric verification produces less correlated errors than single-context same-family review. | An asymmetric verifier subagent produces the same errors as the implementer. |

---

## Three Layers

```
                    ┌──────────────────────────────────────┐
                    │  Layer 3 — Judgmental                │
                    │  Council, cross-family, operator     │
                    │  Triggered by risk_level / pivot     │
                    ├──────────────────────────────────────┤
                    │  Layer 2 — Behavioral                │
                    │  Acceptance criteria, SCAN, scenario │
                    │  Runs on task completion             │
                    ├──────────────────────────────────────┤
                    │  Layer 1 — Structural                │
                    │  Schema, citation, recitation overlap│
                    │  Runs on every event (automatic)     │
                    └──────────────────────────────────────┘
```

A task moves up the pyramid only when triggered. Standard-risk routine work runs Layer 1 and 2 only. Elevated runs all three with a small council. Critical runs all three with a larger council and operator review.

---

## Layer 1 — Structural Checks

**When.** On every event written to `events.jsonl`. Automatic.

**Checks.**

| # | Check | Pass condition |
|---|---|---|
| 1 | Schema validation | The event payload validates against `schemas/artifacts/<kind>.yaml` ∪ `schemas/projects/<name>/artifact-extensions.yaml`. |
| 2 | Citation existence | Every `[KIND-ID#hash]` in the payload resolves to an existing artifact projection. |
| 3 | Citation freshness | Every cited hash matches the current short-hash for that artifact in `hashes.json`. |
| 4 | Frontmatter lint | Required fields present and well-typed (e.g., `risk_level` ∈ {standard, elevated, critical}). |
| 5 | Reference graph | No `consumes:` entry points at a non-existent artifact; no `depends_on:` points at a non-existent task. |
| 6 | Recitation overlap | For every `task.recite` event, Jaccard overlap between paraphrase and source is inside the profile band: `recitation_overlap_floor` ≤ overlap ≤ `recitation_overlap_ceiling`. Below floor: likely unread. Above ceiling: transcribed, not paraphrased. See `core/TYPED-ARTIFACTS.md` §Recitation. |
| 7 | Hash chain | The event's `prev_hash` matches the previous event's `hash`. The event's recomputed hash matches its recorded hash. |
| 8 | Scope completeness | At `session.handoff`, the most recent `scope.complete` event covers every PROJECT.md §Scope item with a `terminal_state` in the schema's `capability-gates.yaml` `scope_completeness.allowed_terminal_states`. Failure codes: `scope_completeness_missing`, `scope_completeness_terminal_state_disallowed`, `scope_completeness_unrepresented_item`. See `core/SUBSTRATE.md` §Scope Completeness. |
| 9 | External state read-back | For every `task.complete` whose task matches a schema's `capability-gates.yaml` `external_state_readback.required_for` pattern, a paired `external_state.read_back` event with the same `task_id` exists within 5 events after the `task.complete`. Failure code: `external_state_readback_missing`. `divergence_detected: true` is a WARNING (not FAIL) and prompts a follow-up `friction.log`. See `core/SUBSTRATE.md` §External State Read-Back. |
| 10 | Bootstrap probe | Every project with a `project.activate` event has either (`bootstrap.inventory_diff` followed by `bootstrap.scope_locked`, with `operator_reconciliation` populated) OR a `bootstrap.probe_skipped` event. Failure code: `bootstrap_probe_missing`. See `core/SUBSTRATE.md` §Bootstrap Inventory Sweep. |
| 11 | execution_mode validity | If `OR-001.delegation_policy.execution_mode` is set, its value is in `{interactive, agent, observer}`. `observer` is reserved (not yet implemented in v5.2.0); the harness emits a WARNING with code `execution_mode_observer_reserved` and treats the dispatch as `interactive` for behavior purposes. Any value outside the enum is a FAIL with code `execution_mode_invalid`. See `core/ATOMICITY.md` §Execution Mode. |
| 12 | Toolchain integrity (v5.2.1) | Before the session's first hash-computing operation, each tool pinned by the most recent `toolchain.anchor` event re-hashes to its recorded `sha256`. Mismatch is a FAIL with code `toolchain_drift`; a missing `toolchain.anchor` in a workspace with any hash-bearing events is a WARNING with code `toolchain_unanchored`. See `core/SUBSTRATE.md` §Toolchain Anchor. |
| 13 | Checked claims (v5.3) | Every `claim:` block present anywhere in the chain (required or not) is structurally well-formed: exactly one known predicate kind, `checked_at`, and `passed` present. FAIL `checked_claims_malformed` otherwise. Additionally, for event kinds a schema's `verification.yaml` `checked_claims.required_for` names, the matching event (or, for `scope.complete`, each `scope_items[]` entry) carries such a block with `passed: true`. FAIL `checked_claims_missing` (block absent or malformed) or `checked_claims_predicate_failed` (block present, well-formed, `passed: false`). This check is about what was *recorded*, not the world as it stands now — see §Claim Replay below for re-evaluation against current state. See `core/SUBSTRATE.md` §Checked Claims. |

| 14 | Event ID integrity (v6.0.0) | Every event `id` is unique across the whole log, and each `EV-<n>` is strictly greater than every ID before it. Gaps are legal; repeats and backwards jumps are not. FAIL `duplicate_event_id` (the report names both line numbers, actors, and projects, because deciding which of two same-named events survives is a judgment about content) or `non_monotonic_event_id`. From the field incident where two agents appended to one chain, the resuming agent derived its next ID from its own project's last event rather than the chain tail, and ten events under five names verified clean because every `prev_hash` was correct. See `core/SUBSTRATE.md` §Deriving the Next Event ID. |
| 15 | Lock enforcement (v6.0.0) | A `project.activate` for project X while project Y holds the Lock, with no intervening `project.park` / `project.archive` for Y, is a FAIL with code `lock_activate_without_release`. Bootstrap (the first activate) and re-activating the project already active (`hw bootstrap --resume`) are legal; `_harness`-scoped meta events never move the Lock. `core/LOCK.md` §The Switch Protocol promised this refusal from v5.0; until v6.0.0 it was prose and a field deployment appended the second activate unchallenged. |
| 16 | `harness_version` gate (v6.0.0) | The active project's schema declares `harness_version` in `schema.yaml`; a value greater than the harness's own `HARNESS_VERSION` is a FAIL with code `harness_version_too_new` and a refusal naming both versions. Older is fine (note `harness_version_older`); absent or unparseable is a note, not a refusal. Scoped to the active project because the Lock guarantees exactly one schema is in force. CONTRIBUTING.md §5 required this from v5.1.1; no code read the field until v6.0.0, which is how a 5.2.1 harness shipped alongside a 5.3.0 schema. |
| 17 | Cycle lifecycle (v6.0.0) | On `lifecycle: ongoing` projects: a `cycle.close` with no matching open (matched by `cycle_id` when both carry one) FAILs `cycle_close_without_open`; a second `cycle.open` with no intervening close FAILs `cycle_open_without_close`; either kind on a project whose PROJECT.md declares (or defaults to) `lifecycle: terminal` FAILs `cycle_on_terminal_lifecycle`; `project.archive` with a cycle still open FAILs `wrap_with_open_cycle`. Parking with an open cycle is legal — an ongoing project parks and resumes like any other. Specified in v5.3 (`core/SUBSTRATE.md` §Lifecycle events, `core/LOCK.md` §Ongoing Projects), implemented in v6.0.0. |
| 18 | Schema-declared Layer 1 checks (v6.0.0) | A schema may declare its own structural checks in `capability-gates.yaml` as a block carrying `layer1_check_name: <name>` and `enforce: true`; the verifier runs the ones it implements for any project whose active schema declares them (CONTRIBUTING.md §4 — core machinery, schema-configured trigger). Implemented: `spawn_pause_skipped`, `registry_status_vs_supersede_chain`, `rollup_citation_stale_or_broken`, all three from `schemas/projects/program/capability-gates.yaml`, where they had existed only as `rule: |` prose. Roll-up citation staleness follows the severities that YAML states: write-time is a hard FAIL, later-cycle re-checks are non-blocking WARNINGs. |
| 19 | Exclusion discipline (v6.0.0) | A hypothesis payload (`status` on a `finding.add`) may be `excluded` only with a `test_ref` naming a dynamic test: an `evidence.capture` id present in the chain, or a `claim:` block on the same event. Absent or empty `test_ref` FAILs `excluded_without_test_ref`; a `test_ref` citing an `ED-NNN` no `evidence.capture` produced FAILs `excluded_test_ref_unresolved`; a `status` outside `{open, suspect, excluded}` FAILs `invalid_hypothesis_status`. Static reads mark `suspect` — the verifier cannot see how a conclusion was reached, so it enforces the one thing it can see: whether anything ran. From AP-008, where a well-argued static read removed the true root cause from the hypothesis list and ~19 attempts were burned before it was revisited. See `core/SUBSTRATE.md` §Exclusion Discipline. |
| 20 | Evidence capture (v6.0.0) | Every `evidence.capture` event carries a well-formed `ED-NNN` id unique across the log, and exactly one content form. FAIL codes: `evidence_id_malformed`, `duplicate_evidence_id`, `evidence_capture_no_content` (neither `content` nor `content_path`), `evidence_capture_content_ambiguous` (both), `evidence_capture_path_without_hash` (`content_path` with no `content_sha256`). Ids are unique across the whole log, not per project, because `test_ref` and finding evidence cite them bare. From the field, where load-bearing command output survived only when hand-copied into a human ledger. See `core/SUBSTRATE.md` §Evidence Capture. |

| 21 | Open loops (v6.0.0) | `loop.close` with no matching `loop.open` for that `loop_id` in the project — including a second close of the same loop — FAILs `loop_close_without_open`. A `loop_id` opened twice in one project FAILs `duplicate_loop_open` (loops are never reopened; a recurrence is a new `L` id). A `session.handoff` whose `open_loops` list omits a loop that is open at that point in the chain FAILs `handoff_missing_open_loops`. An **absent** `open_loops` field is a note (`handoff_open_loops_absent`), not a FAIL — pre-v6 chains keep verifying. Staleness is not checked here: it is date-dependent and belongs to `hw status`, which leads with OVERDUE OPEN LOOPS. From the field incident where a fully-gated server rejoin sat unconsumed for five weeks and surfaced through an unrelated symptom in production. See `core/SUBSTRATE.md` §Open Loops. |

**On failure.** Checks that are read-only computations (schema validation, citation existence/freshness — checks 1–3) run *before* append: the offending payload is rejected with a structured error and nothing lands in the log (v5.2.1; see `core/SUBSTRATE.md` §`hw add` step 3). For defects discovered after an event has already been appended, a `verify.layer1.fail` event is appended *immediately after* the offending event and the harness either:

- **Reject + revert** (default for `task.recite`, and for any `<kind>.add` defect found post-append): the offending event is reversed by an immediate `<kind>.supersede` to null and the projection is removed. Retry.
- **Block** (default for `task.status`): the task transitions to `blocked` with `reason: layer1_fail <check>`.

The agent does not "decide" whether to honor a Layer 1 failure. The substrate enforces; the agent retries or escalates.

**Friction prompt signal.** If the same Layer 1 check fails ≥3 times within a single task on the same `target_id`, the harness emits a `friction.log.prompt` event with `trigger: layer1_repeat`. Read each prompt and decide whether to follow with a `friction.log` event. See `core/SUBSTRATE.md` §Friction Log Event Kind for the full heuristic table.

---

## Claim Replay — `hw verify --claims` (v5.3)

Layer 1's Checked claims row (above) is a structural check: it looks only at what was recorded, at authoring time, inside the event itself. It cannot detect a claim that was true when written and has since rotted — a file moved, a service redeployed, a command's behavior drifted. `hw verify --claims` is **not** a fourth pyramid layer; it is an orthogonal replay pass that answers a different question than every layer above answers: not "is the event log internally consistent" but "is what the log currently asserts about the world still true." See `core/SUBSTRATE.md` §Checked Claims for the `claim:` payload schema and the five predicate kinds.

**When to run it.** Not automatic, and not gated to any risk level or trigger — `--claims` is an operator- or schedule-invoked audit, analogous to running `git fsck` on a schedule rather than as a per-commit hook. Standard use: before an operator review, before archiving a project, or as a periodic sweep on long-running / ongoing (v5.3 lifecycle) projects where the world the claims describe has had time to drift.

**Algorithm.**

1. Walk `events.jsonl` in order. Collect every well-formed `claim:` block from `task.complete`, `finding.add`, and `external_state.read_back` payloads, plus each `scope_items[]` entry of `scope.complete` payloads. Malformed blocks are already reported by Layer 1 check 13; replay does not re-evaluate them (nothing evaluable) and records them as `error: malformed, not replayed`.
2. For each collected claim, re-evaluate `predicate` against the current workspace:
   - `file_exists` / `file_absent` — check the path (relative to workspace root) now.
   - `file_sha256` — recompute the file's SHA-256 now; compare full hex.
   - `url_status` — issue the request now; compare status code. A network failure records `error`, not `fail` — an unreachable URL is missing information, not evidence the claim was false.
   - `cmd_exit` — executed only if **both** gates are open: the operator passed `--allow-cmd`, **and** the claim's project's active schema declares `shell_exec` available (`capability-gates.yaml`; see the shell-capability gate in `core/SUBSTRATE.md` §Checked Claims). Otherwise the claim is recorded `skipped: shell predicates disabled` (default — `--allow-cmd` absent) or `skipped: shell_exec not permitted by workspace capability declarations` (schema gate closed). No active schema, or no `capability-gates.yaml` found, degrades to the closed gate — shell predicates are off by default, not on by default, in the absence of information.
3. Compare the fresh result against the recorded `passed`. `pass` = predicate holds now. `fail` = predicate does not hold now (replay reports the world as it is *now*, regardless of what was recorded at write time). `error` = the predicate could not be evaluated (network failure, unreadable file for reasons other than absence, malformed block). `skipped` = gated off (`cmd_exit` only).
4. Emit a structured report, separate from the integrity report:

```
hw verify --claims <workspace>:
  claims_checked:  <N>
  pass:            <N>
  fail:            <N> [<list of event-id.label: detail>]
  error:           <N> [<list, with reason>]
  skipped:         <N> [<list, with reason>]
  result:          PASS | FAIL | N/A (no claims recorded)
```

`FAIL` requires at least one `fail`. `error` and `skipped` are reported but do not by themselves fail the replay — an unreachable URL or a gated `cmd_exit` is missing information, not a disproven claim. `N/A` when the chain has zero well-formed claims to replay — this is expected and fine (`claim:` is never required by default; see `core/SUBSTRATE.md` §Checked Claims "Never required by default"). The golden fixture (`tools/fixtures/golden-workspace`), for example, has none and reports `N/A`.

**Relationship to the integrity result.** `hw verify --claims` runs alongside, never instead of, the standard integrity replay described in `core/SUBSTRATE.md` §`hw verify`. The two `result` fields are independent: a `--claims` FAIL does not imply chain tampering, and an integrity FAIL (a chain break, a tampered hash) makes claim replay unreliable — a claim's `predicate` came from a payload whose own hash may not be trustworthy — so an agent reading a `--claims` report should check the integrity result first.

---

## Layer 2 — Behavioral Checks

**When.** On `task.complete` events. Before the task is allowed to project to status `complete`.

**Checks.**

| # | Check | Pass condition |
|---|---|---|
| 1 | Acceptance criteria | Each `acceptance_criteria` item in `task.md` frontmatter is independently evaluated; pass/fail recorded. |
| 2 | SCAN compliance | At least one `task.scan` event exists for each `@@SCAN_n_*` marker in the project's compressed rules, recorded *before* the first state-changing event of this task. |
| 3 | Recitation completeness | Every artifact in `consumes:` has at least one corresponding `task.recite` event for this task. |
| 4 | Failure scenario evaluation | If `risk_level ∈ {elevated, critical}` and the task produces end-user-facing content, three realistic failure scenarios are recorded, each evaluated for safety. |
| 5 | Output presence | Whatever the task was supposed to produce exists at the declared path. |

**Acceptance criteria evaluation.** Each criterion is a string. Record, in the completion-report, *how it was evaluated* and *what result was found*. Criteria like "Word count ≤ 300" are mechanically checkable; criteria like "Tone matches brand voice schema X" require judgment. Criteria that require judgment in standard-risk tasks pass on the recorded evaluation; in elevated/critical they additionally trigger Layer 3.

**On failure.** The task transitions to `blocked` with `reason: layer2_fail <check>`. The completion report records which criteria failed. The planner reviews and decides whether to re-task or unblock.

**Friction prompt signal.** Any `verify.layer2.fail` event triggers a `friction.log.prompt` with `trigger: layer2_fail`. Layer 2 failures almost always indicate a substrate or schema gap, not just an agent error. See `core/SUBSTRATE.md` §Friction Log Event Kind.

---

## Layer 3 — Judgmental Review

**When.** Triggered by `risk_level` or by configured pivot points. Never invoked by the agent's self-uncertainty. Self-uncertainty is a `task.status → blocked` event, not a council fire — councils are expensive and the agent's judgment that something feels off is not a structural trigger.

### Council Review

A council is a set of subagents with declared perspectives. Each member reads the same input scope (the task's outputs, its `consumes`, its acceptance-criteria evaluation) but with **context-asymmetric framing**:

- Verifier subagents see the artifacts, the spec, and the acceptance criteria. They do **not** see the implementer's chain-of-thought, intermediate drafts, or rationale prose. This breaks correlated-error patterns where a verifier inheriting the implementer's frame validates the implementer's mistakes.

Example council from `schemas/projects/<name>/council.yaml`:

```yaml
members:
  - role: operator-reality-calibrator
    prompt_template: "Verify that the artifact does not assume budget, timeline, or team capacity beyond what OR-001 declares. Cite specific OR-001 fields. Convergence vote: pass / fail."
  - role: scope-guard
    prompt_template: "Verify that the artifact does not introduce out-of-scope work. Reference PROJECT.md scope and the task's consumes list. Convergence vote: pass / fail."
  - role: anti-pattern-watcher
    prompt_template: "Check the artifact against in-scope anti-patterns (filter AP-* by applies_to). For each AP that could apply, state whether the artifact reintroduces it. Convergence vote: pass / fail."
convergence_rule: all-agree-or-escalate
```

**Trigger sources.**

| Trigger | Source |
|---|---|
| Project bootstrap (Verification Checkpoint) | `project.activate` event. |
| Phase boundary (declared in TASK-STATE.yaml `checkpoint`) | `task.complete` of the last task in a phase. |
| Critical-risk task completion | `risk_level: critical` in task frontmatter. |
| Operator command | `hw council <task-id>`. |

**Trigger-aware prompts.** A council role that fires at multiple triggers (e.g., `project.activate` at bootstrap and `task.complete` later) often needs different prompts at each trigger. At `project.activate` no deliverable exists; the role can only evaluate metadata. At `task.complete` the deliverable does exist; the role evaluates the output. A single prompt written for one trigger applied at the other forces the council member to interpret around it (e.g., "sample the output" when no output exists). The cost: the member fabricates an evaluation, the report passes, and the operator believes the trigger was reviewed when it wasn't.

The schema declares trigger-specific prompts on a council member by replacing `prompt_template:` with a pair (or set) of trigger-keyed templates:

```yaml
members:
  - role: operator-goal-aligner
    prompt_template_on_activate: |
      <metadata-only review prompt for project.activate>
    prompt_template_on_output: |
      <output-review prompt for task.complete / phase.complete / project.archive>
```

The harness selects the prompt by trigger event:

| Trigger event | Selected prompt |
|---|---|
| `project.activate` | `prompt_template_on_activate` |
| `task.complete`, `phase.complete`, `project.archive`, `hw council` | `prompt_template_on_output` |

If a role declares only the legacy `prompt_template:`, the harness falls back to it for all triggers (backwards-compatible). Schemas adopting trigger-aware prompts set both keys; falling through `on_activate → prompt_template` produces the bootstrap-time-vs-output-time mismatch this pattern was added to fix (see report-synthesis council.yaml `operator-goal-aligner`).

### Council Role Library

Reusable roles a schema may include in its `council.yaml`. Each role is opt-in; schemas declare which roles fire and at which triggers.

| Role | When to include | Verifies |
|---|---|---|
| `operator-reality-calibrator` | Most schemas. | Plans, decisions, and outputs respect OR-001 budget, timeline, team, authority. |
| `scope-guard` | Schemas where scope creep is a known risk. | Outputs do not introduce work outside PROJECT.md scope or the task's `consumes` list. |
| `anti-pattern-watcher` | Most schemas. | Outputs do not reintroduce in-scope anti-patterns. |
| `operator-goal-aligner` | Synthesis-style schemas. | Synthesis purpose / target audience match what is actually being produced. |
| `variant-comparison-watcher` | Schemas with tasks declaring `delivery_mode: ab-variant`. Opt-in per task or per schema. | Variants produced under `ab-variant` differ meaningfully on the declared `ab_variant_axis` — pairwise diff exceeds a configurable threshold, no two variants are trivial paraphrases. Single-line PASS/FAIL: variants differ on `<axis>` per pairwise diff against threshold. |
| `soul_consistency_watcher` (v5.2.0) | Schemas where the operator has declared an `operator_soul_anchor` event (see `core/SUBSTRATE.md` §Operator Soul Anchor). Opt-in per schema; default off. Triggers `safety_floor_soul_breach` in `execution_mode: agent` runs (see `core/ATOMICITY.md` §Execution Mode). | The agent has not drifted from operator-declared identity. FAILs on any of: (a) work product proposes a workaround when the real fix is reachable; (b) work product proposes "tabling for later" with no documented blocker; (c) work product presents incomplete work as done; (d) work product fails to clear the operator's named quality bar from the soul anchor. Reads the soul anchor content from the most recent `operator_soul_anchor` event by hash. |

The `soul_consistency_watcher` reads the most recent `operator_soul_anchor` event in the chain, fetches the soul.md content at the event-recorded hash, and compares the work product's prose against the operator's declared anti-patterns and quality bar. The member fires with context-asymmetric framing as usual: it sees the work product, the soul anchor, and the task's spec; it does not see the implementer's chain-of-thought.

If no `operator_soul_anchor` event exists in the chain, the member emits `member_skipped: no_soul_anchor` and the convergence rule treats it as PASS (a missing anchor is not a watcher failure; it is a missing primitive). Schemas that declare `soul_anchor_required: true` reject bootstrap when the anchor is absent, so by the time the watcher fires, the anchor exists or the schema permits its absence.

**Smoke-run marker integration.** The smoke-run safety floor (see `core/ATOMICITY.md` §Execution Mode) shares a marker dictionary with this watcher. If the operator's soul.md anti-patterns name "smoke runs" or equivalent ("simulated demonstrations of work", "would normally"), the watcher's marker set includes those phrases; the same FAIL fires in both the safety floor (interactive mode) and the watcher (council fire). Both surfaces produce a Layer 3 escalation; the operator sees one event, not two duplicate escalations.

The `variant-comparison-watcher` reads the N variant artifacts produced by the task and computes, for each pair, the divergence on the declared axis (lexical diff, structural diff, or domain-specific comparator declared by the schema). PASS if divergence on every pair exceeds the configurable threshold; FAIL otherwise. Convergence rule applies as configured (typically `any-fail-blocks` for ab-variant — a single trivial pair invalidates the differentiated-output premise).

The threshold is intentionally placeholder in v5.1; tuning happens empirically. Schemas may set a per-schema threshold; otherwise the harness uses a coarse default (Jaccard distance ≥ 0.4 between variant body tokens, after dropping the variant-identifier scaffolding).

**Convergence rules** (declared per schema):

- `all-agree-or-escalate` — every member must vote `pass`. One `fail` escalates to operator.
- `majority-or-escalate` — majority `pass` confirms; ties or majority-fail escalate.
- `any-fail-blocks` — any `fail` blocks; identical to all-agree but framed for high-stakes work.

The harness writes `council.invoke` at trigger, `council.report` for each member's finding, and either `council.converged` (proceed) or `council.escalated` (operator decides).

**Council projection.** Per fire, the harness regenerates `projects/<id>/council/<fire_id>-<trigger>.md` from the council events grouped by `fire_id`. An aggregate `projects/<id>/council/INDEX.md` lists fires chronologically. See `core/SUBSTRATE.md` §Council Report Projection.

**Friction prompt signal.** A `council.escalated` event whose subject task has `risk_level: critical` emits a `friction.log.prompt` with `trigger: council_non_convergence_critical`. Critical-risk non-convergence is a strong signal that the schema's council composition or convergence rule mis-specifies the task's review needs.

### Cross-Family Verification (Opt-In)

If the operator configures multiple AI families (e.g., Claude + Copilot CLI), council members can be drawn from different families. Family diversity is configured per role:

```yaml
members:
  - role: scope-guard
    family: copilot                  # forces this member to a Copilot subagent
    prompt_template: "..."
```

Default: same-family with context asymmetry. Cross-family is opt-in for operators with the infrastructure.

### Operator Review

Escalates when:

- Council reaches `escalated` outcome.
- A Layer 1 or Layer 2 check fails repeatedly past retry budget (default: 3).
- A schema-declared pivot trigger fires (e.g., "operator review required after Phase 2 closes").

The operator's decision is recorded in a `task.status` event with `actor: operator`. Operator review does not bypass the substrate; it writes events like any actor.

---

## Risk Levels

```yaml
# In schemas/projects/<name>/verification.yaml
standard:
  layers: [1, 2]
  retry_budget: 3
elevated:
  layers: [1, 2, 3]
  council_size: 2
  failure_scenarios_required: 3
  retry_budget: 2
critical:
  layers: [1, 2, 3]
  council_size: 3
  cross_family: false      # opt-in
  operator_review_required: true
  failure_scenarios_required: 3
  retry_budget: 1
```

Risk levels are declared at task authoring (planner) and **locked**. Mid-execution escalation is not a substitute for correct authoring; if the planner authored the wrong level, the task is `blocked`, the planner re-authors with the correct level, and the executor restarts.

`failure_scenarios_required: 3` is a hard count, not a target. Three realistic scenarios is what the empirical bar in v4.1.1 §7 was sized at; v5.0 inherits the count and makes the failure mode explicit (a single failed scenario blocks the task).

---

## What "Pushback" Becomes

v4.1.1 made Pushback a runtime default — every task ran a pre-execution sanity check for "does this make sense." The cost: low-signal interventions on standard-risk routine work. The agent paused at every task, generated a one-paragraph "this looks fine to proceed," and the operator skimmed and approved. Two minutes per task, dozens of tasks, hours of operator time burned on verbal acknowledgement.

v5.0 makes Pushback a Layer 3 trigger:

- **Council non-convergence** → escalate. The pushback is structural: members disagree, and the agent does not "decide" who's right.
- **Repeated Layer 1/2 failure** → escalate. The pushback is automatic: if the substrate keeps rejecting, escalate.
- **Configured pivot** → escalate. The pushback is scheduled by the schema, not the agent's vibe.

Standard-risk routine work does not invoke pushback at all. The earlier behavior of "before each task, the executor evaluates whether the instructions make sense" produced a lot of low-signal interventions; replacing it with structural triggers reduces the operator-pull-in rate.

If a *blocking ambiguity* is encountered mid-execution, the response is `task.status → blocked` with a reason, not Pushback. Pushback existed in v4.1.1 as a verbal request to the agent ("evaluate before executing"); v5.0 replaces verbal requests with substrate-level events.

---

## What Verification Is NOT

| Not | Because |
|---|---|
| Automated end-to-end testing of the deliverable. | Verification is structural about the harness's contract; deliverable testing is a project concern declared in acceptance criteria. |
| Full re-execution or re-testing of the deliverable, even with `hw verify --claims`. | Claim replay re-checks only the specific predicates an agent chose to record — a targeted spot-check of asserted world-state, not exhaustive deliverable testing. See `core/SUBSTRATE.md` §Checked Claims. |
| A safety net that lets shoddy work through. | A Layer 1 failure is non-negotiable; the work cannot move forward. |
| A blanket review queue. | Layer 3 fires on triggers, not on every task. |
| Human-in-the-loop by default. | Standard risk runs Layer 1 + 2 without operator. Elevated and critical tasks bring the operator in. |

---

## Relationship to Other Mechanisms

| Mechanism | Interaction |
|---|---|
| Substrate | Verification reads events and projections; it does not write to the Mutable Surface. Layer 1 check 13 and `hw verify --claims` read the `claim:` blocks defined in `core/SUBSTRATE.md` §Checked Claims. |
| Lock | Council fires at `project.activate` (Verification Checkpoint). Layer 1 check 15 enforces `core/LOCK.md` §The Switch Protocol; check 17 enforces the ongoing-lifecycle cycle rules. |
| Atomicity | Risk level is a task field; it determines which layers run. |
| Typed Artifacts | Layer 1 citation freshness uses the artifact hash sidecar. |
| Precedence | Tier 1 rules treated as `risk_level: critical` for any task that produces output covered by them. |
