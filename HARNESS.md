# HyperWorker v6.0.0

> **Read this file first.** It is the entry point. An AI agent that reads only this file learns what HyperWorker is, where the parts live, and how to bootstrap a project. Stop after this file only when you do not yet need to act; before any state-changing operation, read `core/SUBSTRATE.md` too.

A project management harness for AI agents. The thesis: frontier harnesses succeed by making agent compliance **structurally enforceable**, not verbally requested. Verbal rules ("be careful," "do not skip steps," "don't fabricate citations") drift the moment context fills. Structural primitives — hash-cited artifacts, append-only events, capability-gated subagents, verification pyramids — do not.

v5.0 was a clean break from v4.1.1. v5.0.1 closed documentation and template gaps surfaced by a strategic-foundation synthesis run. v5.1 added structural primitives surfaced by a second empirical run (friction-log event kind, council-report projection, session-handoff event kind, ab-variant delivery mode, delegation-policy and model-selection-policy OR fields, synthesis T-001 corpus-scan task). v5.1.1 added five Layer 1 primitives surfaced by an asset-update run on a real CMS (`scope.complete` events, `external_state.read_back`, bootstrap inventory sweep, edit-vs-create-vs-delete enumeration, redirect-coverage rollup).

---

## Quick Start

1. Point an AI agent at this repository.
2. Say: *"Read `HARNESS.md` and bootstrap a project from the `<schema-name>` schema for `<short description>`."*

The agent reads this file, picks (or asks about) a schema from `schemas/projects/`, and follows the Bootstrap Protocol below. No prerequisites; no install step. The agent operates the harness by reading and writing files.

---

## Architecture

```
                    ┌──────────────────────────┐
                    │      Lock                │  Single project focus
                    ├──────────────────────────┤
                    │      Atomicity           │  One task / hermetic / capability-gated
                    ├──────────────────────────┤
                    │      Typed Artifacts     │  Decisions, anti-patterns, findings,
                    │                          │  operating-reality + consumption protocol
                    ├──────────────────────────┤
                    │      Verification        │  Cheap structural → mid behavioral →
                    │      Pyramid             │  high judgmental (council)
                    ├──────────────────────────┤
                    │      Precedence          │  Tiered rule conflict resolution
                    └──────────────────────────┘
                    ──────────────────────────────
                            SUBSTRATE
                    ──────────────────────────────
              events.jsonl │ projections │ hashes │ git
                    ──────────────────────────────
```

Five mechanisms. One substrate. The substrate is event-sourced state with regenerable file projections; mechanisms compute against it. Every primitive that survives is one that does not depend on the agent's word — hashes, citations, schemas, event records.

| Mechanism | Solves | File |
|---|---|---|
| Lock | Drift across multiple "active" projects | [core/LOCK.md](core/LOCK.md) |
| Atomicity | Oversize tasks, polluted parent context, missing tools in subagents | [core/ATOMICITY.md](core/ATOMICITY.md) |
| Typed Artifacts | Lost decisions, mutable-memory pipeline failures, citation drift | [core/TYPED-ARTIFACTS.md](core/TYPED-ARTIFACTS.md) |
| Verification | Unproven completion, stacked-cost reviews | [core/VERIFICATION.md](core/VERIFICATION.md) |
| Precedence | Rule conflicts | [core/PRECEDENCE.md](core/PRECEDENCE.md) |
| **Substrate** (not a mechanism — the medium) | State disagreements, untraceable changes | [core/SUBSTRATE.md](core/SUBSTRATE.md) |

---

## What is `hw`?

**`hw` is an agent protocol, not a CLI.** When this repo says `hw add decision < draft.md`, it means: *the agent performs the file-system protocol described in `core/SUBSTRATE.md` §`hw add`* — append a JSON event line to `events.jsonl`, render the projection, update `hashes.json`. There is no binary to install. Any agent that can read markdown and append to a file executes every `hw` operation.

The full set of `hw` operations and their protocols is documented in `core/SUBSTRATE.md`. Read it once before the first bootstrap.

---

## File Structure

### Truth Layer (harness infrastructure — never edit during execution)

```
HARNESS.md                           # this file
core/
  SUBSTRATE.md                       # event log + projections + hashes + hw protocols
  LOCK.md
  ATOMICITY.md                       # includes branch/fold + capability gates
  TYPED-ARTIFACTS.md                 # decisions / findings / anti-patterns / operating-reality + consumption protocol
  VERIFICATION.md                    # pyramid + risk classification + council
  PRECEDENCE.md                      # tiered rules + SCAN markers
templates/
  executor-prompt.md                 # under 30 lines; substrate carries the rest
  task-template.md
  project-template.md
  rules-template.md
  artifact-templates/
    decision-template.md
    finding-template.md
    anti-pattern-template.md
    operating-reality-template.md
    evidence-capture.md              # v6.0.0 projection of one evidence.capture event
  models/                            # per-model harness profiles
    default.yaml
    claude-opus-4-7.yaml
    claude-opus-4-6.yaml
    claude-sonnet-4-6.yaml
    claude-haiku-4-5.yaml
    github-copilot.yaml
    _ranking.yaml                    # operator ranking override (v5.1, optional)
    README.md
  session-handoff-template.md        # canonical SESSION-HANDOFF.md projection format
  CYCLES.md                          # canonical CYCLES.md projection format (lifecycle: ongoing)
  ELIMINATION.md                     # canonical ELIMINATION.md projection format (v6.0.0)
schemas/
  artifacts/                         # default artifact schemas (decision, finding, anti-pattern, operating-reality)
  projects/                          # project schemas with bootstrap-ready scaffolds
    marketing-campaign/              # full port from v4.1.1 case study 01
    software-feature-ship/
    client-onboarding/
    event-planning/
    compliance-audit/
    report-synthesis/
    site-review-repair/
    site-seo/
    site-monetization/
    gov-bid-hunt/
    opportunity-hunt/
    lead-mining/
    single-opportunity/
    cleanroom-rebuild/
    brand-ecosystem-audit/
    market-gap-intelligence/
    content-piece-test/
    book-edit-test/
    course-master-plan-test/
    program/                         # orchestrate N workstream instances (v5.3)
reference/
  VALIDATION.md
  FAILURE-MODES.md
  field-reports/                     # per-machine field-gather reports (genericized evidence)
tools/
  hw-verify.py                       # reference implementation of `hw verify`
  make-golden-fixture.py             # regenerates the pinned regression fixture
  fixtures/
    golden-workspace/                # pinned 7-event reference project (regression signal)
CHANGELOG.md
VISION.md
README.md
CONTRIBUTING.md
LICENSE
```

### Mutable Surface (project content — edited as the work proceeds)

```
.hyperworker/
  events.jsonl                       # canonical event log
  hashes.json                        # projection hash sidecar
  config.yaml                        # active model profile, schema source
  agents/                            # subagent capability declarations
  models/<active-profile>.yaml       # frozen copy of the active per-model profile
projects/
  active_project.md                  # projection
  <project-id>/
    PROJECT.md                       # canonical narrative
    00-REFERENCE-rules.md            # canonical narrative + SCAN markers
    00-REFERENCE-rules.compressed.md # projection (agent prompt loads this)
    config.yaml                      # project-local overrides
    decisions/                       # projections
    findings/                        # projections
    anti-patterns/                   # projections
    operating-reality/               # projections
    council/                         # projections (v5.1) — per-fire markdown + INDEX.md
    SESSION-HANDOFF.md               # projection (v5.1) of the latest session.handoff event
    ELIMINATION.md                   # projection (v6.0.0) of hypothesis status/test_ref
    evidence/                        # projections (v6.0.0) — one file per evidence.capture
    tasks/<task-id>/
      task.md                        # canonical instructions
      consumed-inputs.md             # projection (recitation)
      branches/<branch>/
    done/                            # completed tasks + post-mortems
  archive/                           # archived projects
backlog.md                           # projection
friction-log.md                      # projection (v5.1) of friction.log events; workspace-scoped by default
config.yaml                          # deployment-wide config
```

### Boundary Rule

| Category | Authority |
|---|---|
| Event-sourced (`events.jsonl`) | Canonical. Append-only. |
| Projections (`decisions/`, `findings/`, `TASK-STATE.yaml`, `hashes.json`, …) | Regenerable. Never authoritative. |
| Mutable Surface (`PROJECT.md`, `00-REFERENCE-rules.md`, `task.md` instructions, post-mortem prose) | File-canonical. Versioned via git. |

If unsure, check `core/SUBSTRATE.md` §Boundary Rule.

---

## Friction Logs

Friction logs capture what was unclear, what required training-derived gap-filling, what felt ceremonial, what surprised the operator, and what worked well. The failure mode is post-hoc reconstruction: at the end of a run, the operator tries to remember every place the harness rubbed wrong. Memory loses the specifics; the log gets vague generalities; the next patch cycle misses the actual fixes.

v5.1 makes friction capture a substrate event kind (`friction.log`). Capture is structural rather than operator-instructed.

### The protocol (one step)

**Append one `friction.log` event with a `note`. That is the whole thing.**

```
note: "The recitation band rejected three honest paraphrases in a row."
```

No artifact file. No projection to hand-write. `category`, `severity` and `task_id` are optional — add them if they are already in your head, skip them if they are not. Promoting a friction into an anti-pattern or a finding is a **later, optional** act, done if and when the friction turns out to matter.

Why so bare: a ten-week deployment produced **four** friction entries in 130 events. The mechanism existed and the operator wanted it; filling six fields felt heavier than the value, so the run's best lessons went uncaptured. A one-line note that gets written beats a structured entry that does not. The pre-v6 six-field form still verifies and is still available for anyone who wants it (see `core/SUBSTRATE.md` §Friction Log Event Kind).

| Default location | Path | Use |
|---|---|---|
| Workspace | `friction-log.md` at workspace root | Default. Projection of `friction.log` events scoped to the workspace. |
| Per-project | `projects/<id>/friction-log.md` | Per-project log when the project's `config.yaml` declares `friction_log_scope: project`. |

The projection regenerates from `friction.log` events on every new entry. Hand-edits are overwritten on next regeneration; new entries are recorded by appending `friction.log` events (`hw add friction-log < draft.md`-style protocol; see `core/SUBSTRATE.md` §Friction Log Event Kind for the payload schema).

**Substrate auto-prompts.** The harness emits `friction.log.prompt` informational events when observable signals fire: Layer 1 verification failing on the same check ≥3 times in a task, Layer 2 verification failing, agent output containing training-fill markers, an operator mid-flow directive captured as a Decision, or council non-convergence on a critical-risk task. Read each prompt and decide whether to follow with an actual `friction.log` event. See `core/SUBSTRATE.md` §Friction Log Event Kind for the heuristic table.

**Categories (optional).** A slim entry may carry any `category` string, or none. The pre-v6 rich form's `type` vocabulary is: `REGRESSION` (something that worked before broke), `CONFIRMATION` (a previously-logged friction was resolved by a patch), `NEW-SCHEMA` (the friction is schema-specific), `NEW-CROSS` (cross-schema; affects multiple schemas), `TRAINING-FILL` (the agent filled a gap from training rather than the harness), `OPERATOR-CONFUSION` (the operator was unsure what the harness expected).

The pre-v5.1 working-artifact form (`bootstrap-friction-log.md`) is retained for projects that started under v5.0 / v5.0.1 and have not yet emitted any `friction.log` events; on the first event, the projection switches to `friction-log.md`.

---

## Bootstrap Protocol

When asked to build a harness for a goal, execute these seven steps in order. Do not skip Step 1; do not infer Step 2 without operator confirmation; do not run `bootstrap_questions` from a schema the operator has not endorsed.

1. **Understand the goal.** Ask: project description, domain, constraints. If the operator names a schema, skip to Step 3.
2. **Match a schema.** Suggest one of the default schemas in `schemas/projects/` (see the README schema table: marketing-campaign, software-feature-ship, client-onboarding, event-planning, compliance-audit, report-synthesis, site-review-repair, site-seo, site-monetization, gov-bid-hunt, opportunity-hunt, lead-mining, single-opportunity, cleanroom-rebuild, brand-ecosystem-audit, market-gap-intelligence, content-piece-test, book-edit-test, course-master-plan-test, program). For work with no terminal state, note the schema's `lifecycle: ongoing` option; for many concurrent workstreams under one goal, suggest `program` (see `core/LOCK.md` §Programs). If none fit, offer a custom build that scaffolds from default templates and saves the result with `hw schema save` after the project completes.
3. **Bootstrap:** `hw bootstrap --schema <name> --name <project-id>`. Protocol in `core/SUBSTRATE.md` §`hw bootstrap`. Ask only the questions the schema declares in `schema.yaml` — typically operating-reality (budget, timeline, team, authority), specific rules content, and project description.
4. **Write operating-reality.** Each schema-declared question maps to a field in `OR-001`. Run `hw add operating-reality < draft.md` to append the event and render the projection.
5. **Anchor operator identity (if declared).** If `OR-001.soul_anchor_path` is non-null, read the file at that path. If null and `soul.md` exists at workspace root, read it (v5.2.0 default behavior; hard-enforcement via a schema-declared `soul_anchor_required` field is deferred to v5.2.1 per CHANGELOG v5.2.0.1 §Deferred). Compute SHA-256 of the file's bytes; emit `operator_soul_anchor` with `{soul_path, soul_hash, version: "1.0.0", fired_at}`. See `core/SUBSTRATE.md` §Operator Soul Anchor. If no soul.md exists, skip — the harness fires no event and council fires that include `soul_consistency_watcher` will skip the member with `member_skipped: no_soul_anchor`.
6. **Verification Checkpoint with council.** The schema's `council.yaml` declares a `project.activate` trigger. Council members run with context-asymmetric framing (see `core/VERIFICATION.md` §8.4). Each emits a `council.report`; the convergence rule decides. Surface a single brief summary to the operator, not three free-form questions.
7. **Execute.** The operator runs `hw next-step` or invokes the first task. The first task's `consumes:` list typically references `OR-001` only; downstream tasks consume artifacts produced by earlier ones.

You will know bootstrap finished when: `OR-001` exists, `00-REFERENCE-rules.md` exists, the soul anchor was either fired (if soul.md is declared) or skipped (recorded as no-soul-anchor in the next council fire), the council fired and converged (or escalated to operator), and `hw next-step` returns the first task.

### Operator mid-flow directives

The operator will issue instructions during bootstrap (or mid-task) that do not fit the schema's `bootstrap_questions` — e.g., "use the browser when needed", "Example Corp IT and Example Corp are separate companies", "treat anything from the 2025 audit as primary." The failure mode is treating these as conversation: they affect project structure or scope, but they leave no trace once the conversation context turns over. Tasks downstream cannot cite them. The next session re-litigates them or silently violates them.

Capture each as a typed Decision artifact, verbatim, before the next state-changing event:

1. Recognize a directive that affects project structure or scope.
2. Draft a Decision artifact body capturing the directive **verbatim** (or with explicit paraphrase markers — see Tier 1 verbatim quotation principle in `schemas/projects/<name>/rules-template.md`).
3. `hw add decision < draft.md` with an appropriate `synthesis_role` or schema-specific role (typical values: `scope-decision`, `weighting-rule`, `inclusion-exclusion`).
4. Subsequent tasks consume the new DEC by citation.

The cost is one event per directive — under 30 seconds. The cost of letting a directive stay loose is rediscovering it three sessions later when the artifact it should have constrained ships wrong. The friction log entry A-12 motivates this convention.

---

## Standard Commands

| Command | Behavior |
|---|---|
| `hw bootstrap --schema <name> --name <id>` | Scaffold project from schema. |
| `hw schema save --from <project> --as <name>` | Extract reusable schema from current project. |
| `hw add <kind> < file` | Append typed-artifact event; render projection; update hash. |
| `hw write <task-id> --status <state>` | Task state transition. |
| `hw branch <task-id> <name>` | Open exploratory subtask. |
| `hw fold <task-id>/<branch> --result <text>` | Collapse branch into 1–3 sentence projection in parent. |
| `hw promote <artifact-id>` | Mark provisional → validated. |
| `hw verify` | Replay-with-hash; report integrity. |
| `hw project` | Force projection regeneration from events. |
| `hw council <task-id>` | Manual council invocation. |
| `hw next-step` | Read state, find next pending task with deps met. |
| `hw status` | Project state, blockers, pending council. |
| `hw log <text>` | Backlog intake (no project activation). |
| `hw wrap` | Project completion protocol. |
| `hw park` | Demote active project to backlog. |

Every command has a documented protocol in `core/SUBSTRATE.md`. Operate them by reading and writing files; no binary required.

---

## Per-Model Profiles

Different models respond differently to the same harness primitives. v5.0 ships profiles for the major frontier models so harness behavior adapts declaratively. See `templates/models/README.md` for the field reference and the override-precedence rules. The active profile is selected at scaffold time and frozen into `.hyperworker/models/`.

Profiles document what each model does *differently*, not which is "better." Where a model's behavior is documented in a postmortem (e.g., Anthropic's 2026-04-23 4.7 postmortem on suppress-concise-directives), the profile cites it. Operators add profiles over time; the directory is a library, not a fixed set.

---

## Startup Validation

Before delegating any task, confirm:

- `HARNESS.md`, `core/SUBSTRATE.md` readable.
- `.hyperworker/events.jsonl` exists (or is empty for a fresh init).
- `.hyperworker/config.yaml` declares an active model profile.
- `projects/active_project.md` resolves to a project with `PROJECT.md`, `00-REFERENCE-rules.md`, and at least one task.
- `hw verify` returns `OK` (or, on a fresh project, an empty-log `OK`).

If any check fails, STOP. Report what is missing. The operator resolves before execution begins.

---

## Core Principles

1. **Substrate over rules.** Every primitive that survives is one verifiable without asking the agent if it complied. Rules that ask are ceremonies. Substrate that enforces is structure.
2. **Heavy upfront, light ongoing.** Setup carries the cost; runtime is autonomous. The operator pays once at bootstrap, not at every phase boundary.
3. **Append-only events; regenerable projections.** Knowledge is not "managed" via lifecycles; it is recorded and superseded. The supersede chain is visible; deletion is not.
4. **Five mechanisms plus substrate.** No sixth mechanism without a falsifiable hypothesis and a structural check.
5. **Theory, not finding.** Each primitive is a hypothesis (see `core/*.md` §Hypothesis sections). v5.1 retires whatever fails its falsifier in real use.
