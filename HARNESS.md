# HyperWorker v6.0.0

> **Read this file first. It is the entry point for any agent, from any vendor.** The next four sections are what you need before you touch anything. Everything after them is detail you can come back for.

## What this is

HyperWorker is a project-management harness for AI agents. It is a repository of markdown and YAML — no install, no binary, no service to call. You operate it by reading files and appending lines to a file.

State lives in one append-only event log, `.hyperworker/events.jsonl`. Every human-readable file that summarizes state — a decision, a task list, a ledger — is a **projection**: regenerated from the log, never authoritative. When a projection and the log disagree, the log is right.

The thesis is that agent compliance should be **structurally enforceable, not verbally requested**. Verbal rules ("be careful", "don't skip steps") drift the moment context fills. Hashes, citations, schemas, and event records do not: they can be checked without asking you whether you complied.

This file names no AI product, assumes no particular toolset, and assumes nothing about how much you can hold at once. What you can actually *do* is something you declare and the harness gates on — see §If you are not the usual agent.

## The five things you must never do

Each one is a failure that already happened, in production, at cost.

1. **Never edit the Truth Layer during execution.** `HARNESS.md`, `core/`, `templates/`, `schemas/`, `tools/` are harness infrastructure; project work never rewrites them. Never hand-edit a projection either — it is overwritten on the next regeneration, and your edit is silently gone. Write to the Mutable Surface (`PROJECT.md`, rules, task instructions) or append an event. See §Boundary Rule.
2. **Never append to a chain you do not own.** One `events.jsonl` has at most one writer at any moment. If you are a parallel actor — a delegated subagent, a council member, a sibling session — write a **draft file** in your own directory and let the single convergence writer append. Concurrency lives *between* harness instances, never inside one. See `core/SUBSTRATE.md` §Single-Writer Rule.
3. **Never mark a hypothesis `excluded` without a test.** A careful static read is an argument, not a test; it lands at `suspect` and no further. `excluded` requires a `test_ref` naming something that actually ran — an `evidence.capture` id, or a claim predicate that was evaluated. Ruling a cause out is the most expensive thing you can do, because everything after it is searched somewhere else. See `core/SUBSTRATE.md` §Exclusion Discipline.
4. **Never put a secret in an event.** The log is append-only, so a credential written into it is permanent; the only remediation is rotating it in the real world. Store by reference: `[REDACTED-SECRET]` plus a pointer to where the value lives. `hw add` refuses the append on a hit. See `core/SUBSTRATE.md` §Secrets Gate.
5. **Never claim posted, delivered, or done without re-reading it at the destination.** Not the copy's return code, not the absence of an error, not the source file still being there — the destination path, read back. "Posted" and "received" are different facts. See `core/SUBSTRATE.md` §Transport Rules.

## Recovery Order — how you start, every time

Whether you are bootstrapping, resuming a project, or picking up after context was compacted, read in this order and **stop as soon as you can act**:

1. **`hw verify`.** If the chain is broken, nothing below it is trustworthy. Fix that first.
2. **`projects/<id>/LEDGER.md`.** The generated newest-first digest: what was done, decided, found, opened and closed, in reverse order. One screen usually answers "where are we."
3. **`projects/<id>/SESSION-HANDOFF.md`.** The closing agent's transfer: open operator questions, open loops, the recommended first action.
4. **The task** — `task.md`, plus exactly what its `consumes:` list names, plus the project's rules file. Nothing else is mounted; that is deliberate (`core/ATOMICITY.md` §Hermetic Working Set).

Then, and only as the work actually needs them: raw artifacts, `OPEN-LOOPS.md`, `ELIMINATION.md`. `events.jsonl` comes **last**, and only when two things above disagree. It is the authority, not the reading path: it answers *what happened*, and replaying it to answer *where are we* costs about what doing the work again costs.

The order is field-derived. Across a ten-week deployment a newest-first ledger beat the event log for context recovery every time; the closing interview ranked the log last. v6.0.0 generates the ledger rather than asking anyone to maintain one (`core/SUBSTRATE.md` §Narrative Ledger).

Before your first **state-changing** operation, also read `core/SUBSTRATE.md` — it is the protocol for every `hw` operation.

## If you are not the usual agent

Nothing here is written for one model or one vendor, and nothing adapts to you automatically. If you are new to this workspace, declare what you can do at session start rather than discovering it mid-task:

1. **Write or refresh `.hyperworker/agents/<your-agent-id>.yaml`** with a `provides:` list of the tool capabilities you actually have (`file_read`, `file_write`, `web_browse`, `shell_exec`, …). This file is the input to the capability gate, not a description of you — it is compared against each task's `required_tools`. See `core/ATOMICITY.md` §Capability Gates.
2. **Name yourself in the session record.** The `actor` field on the events you write, and `closing_actor` on the `session.handoff` you write when you stop, are how the next agent knows who did what. If you are not the agent the last handoff assumed, say so there.
3. **When you cannot meet a gate, emit `capability.gap` — do not improvise.** If a task's `required_tools` is not a subset of your `provides:`, the correct move is the gap event naming the missing tools, so the operator can run it in-line, extend a profile, or dispatch elsewhere. Substituting a tool you were not granted is the failure the gate exists to prevent.
4. **If a protocol here is genuinely ambiguous for your environment, append a one-line `friction.log` and keep going.** Guessing silently is what makes a harness undiagnosable. One line is the whole obligation.

There is no per-model guide to find, and there is no hidden instruction set you are missing. If a rule matters, it is enforced by a schema, a required template field, or a `hw verify` FAIL — not by a document you were supposed to have read.

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
  TOOLS.md                           # tools-catalog contract (v6.0.0) — check before building; verify hash, then check predicate; never a dependency
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
  OPEN-LOOPS.md                      # canonical OPEN-LOOPS.md projection format (v6.0.0)
  LEDGER.md                          # canonical LEDGER.md projection format (v6.0.0)
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
    LEDGER.md                        # projection (v6.0.0) — newest-first narrative digest; read first
    SESSION-HANDOFF.md               # projection (v5.1) of the latest session.handoff event
    ELIMINATION.md                   # projection (v6.0.0) of hypothesis status/test_ref
    OPEN-LOOPS.md                    # projection (v6.0.0) of loop.open / loop.close
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

A friction log captures what was unclear, what you had to fill in from training rather than from the harness, what felt like ceremony, and what surprised the operator. The failure mode it prevents is post-hoc reconstruction: at the end of a run nobody remembers the specifics, so the next patch cycle fixes the wrong things. Capture is a substrate event kind (`friction.log`), not a habit anyone has to remember.

### The protocol (one step)

**Append one `friction.log` event with a `note`. That is the whole thing.**

```
note: "The recitation band rejected three honest paraphrases in a row."
```

No artifact file. No projection to hand-write. `category`, `severity` and `task_id` are optional — add them if they are already in your head, skip them if they are not. Promoting a friction into an anti-pattern or a finding is a **later, optional** act, done if and when the friction turns out to matter.

Why so bare: a ten-week deployment produced **four** friction entries in 130 events. The mechanism existed and the operator wanted it; filling six fields felt heavier than the value, so the run's best lessons went uncaptured. A one-line note that gets written beats a structured entry that does not.

The projection lands at `friction-log.md` at workspace root, or `projects/<id>/friction-log.md` when the project's `config.yaml` declares `friction_log_scope: project`. It regenerates from events; hand-edits are overwritten.

The rest is owned by `core/SUBSTRATE.md` §Friction Log Event Kind: the payload schema, the pre-v6 six-field form (still accepted, so no chain migrates), the optional category vocabulary, and the `friction.log.prompt` heuristics that make the harness ask instead of hoping someone remembers.

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

## Model Profiles

`templates/models/*.yaml` are **declarative config the harness reads, not guides an agent reads about itself.** A profile sets a handful of thresholds — the recitation overlap band, when to warn on context fill, default council size, the cost/capability/speed ranks `model_selection_policy` resolves against. The operator picks one at scaffold time; it is frozen into `.hyperworker/models/`. `default.yaml` is deliberately conservative and is the right answer whenever the running model is unknown or the roster is mixed.

There is deliberately **no per-model instruction document** anywhere in this repo, and adding one is out of scope (`VISION.md`). Agents reliably read the entry point and whatever a task forces them through, and nothing else — so a document explaining how *your* model should behave is a document that will not be read at the moment it matters. Anything that must hold for every agent is enforced structurally instead: a schema field, a required template section, or a `hw verify` FAIL.

Field reference and override precedence: `templates/models/README.md`. Profiles record what a model does *differently*, never which is "better"; the directory is a library operators extend, not a fixed set.

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
