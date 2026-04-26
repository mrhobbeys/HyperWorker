# HyperWorker v5.0

> **Read this file first.** It is the entry point for the harness. An AI agent that reads only this file should learn what the harness is, where the parts are, and how to bootstrap a project.

A project management harness for AI agents. v5.0 is a clean break from v4.1.1, not an iteration. The thesis is that frontier harnesses succeed by making agent compliance **structurally enforceable** rather than verbally requested.

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

Five mechanisms. One substrate. The substrate is event-sourced state with regenerable file projections; mechanisms compute against it. Every primitive that survives is one that doesn't depend on the agent's word — hashes, citations, schemas, event records.

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

**`hw` is an agent protocol, not a CLI.** When this repo says `hw add decision < draft.md`, it means: *the agent performs the file-system protocol described in `core/SUBSTRATE.md` §`hw add`* — append a JSON event line to `events.jsonl`, render the projection, update `hashes.json`. There is no binary to install. Any agent that can read markdown and append to a file can execute every `hw` operation.

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
  models/                            # per-model harness profiles
    default.yaml
    claude-opus-4-7.yaml
    claude-opus-4-6.yaml
    claude-sonnet-4-6.yaml
    claude-haiku-4-5.yaml
    github-copilot.yaml
    README.md
schemas/
  artifacts/                         # default artifact schemas (decision, finding, anti-pattern, operating-reality)
  projects/                          # project schemas with bootstrap-ready scaffolds
    marketing-campaign/              # full port from v4.1.1 case study 01
    software-feature-ship/
    client-onboarding/
    event-planning/
    compliance-audit/
reference/
  FAILURE-MODES.md
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
    tasks/<task-id>/
      task.md                        # canonical instructions
      consumed-inputs.md             # projection (recitation)
      branches/<branch>/
    done/                            # completed tasks + post-mortems
  archive/                           # archived projects
backlog.md                           # projection
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

Operators and agents may keep a friction log capturing what was unclear, what required training-derived gap-filling, what felt ceremonial, and what worked well. Friction logs are working artifacts (not event-sourced); they feed the next harness patch cycle.

| Default location | Path | Use |
|---|---|---|
| Workspace | `bootstrap-friction-log.md` at workspace root | One log per workspace covering bootstrap and cross-project friction. The default. |
| Per-project | `projects/<id>/friction-log.md` | Per-project log when friction is project-scoped (e.g., a long synthesis spanning multiple sessions). |

Use the workspace-root log unless the project explicitly opts into per-project scoping. Friction logs are file-canonical (Mutable Surface), versioned via git when available; they are not regenerable from events. See `core/SUBSTRATE.md` §File Locations.

The structure is open; recommended categories from prior runs: (A) harness unclear/incomplete, (B) agent drew on training to fill a gap, (C) steps that felt ceremonial, (D) operator confused or asked for clarification, (E) things that worked well.

---

## Bootstrap Protocol

When asked to build a harness for a goal, the agent:

1. **Understands the goal.** Asks the operator: project description, domain, constraints. If the operator names a schema, skip to step 3.
2. **Matches a schema.** Suggests one of the five default schemas in `schemas/projects/`. If none fit, offers a custom build that scaffolds from default templates and saves the result with `hw schema save` after the project completes.
3. **Bootstraps:** `hw bootstrap --schema <name> --name <project-id>`. The protocol is in `core/SUBSTRATE.md` §`hw bootstrap`. The agent asks only the questions the schema declares in `schema.yaml` — typically operating-reality (budget, timeline, team, authority), specific rules content, and project description.
4. **Writes operating-reality.** Each schema-declared question maps to a field in `OR-001`. The agent runs `hw add operating-reality < draft.md` to append the event and render the projection.
5. **Verification Checkpoint with council.** The schema's `council.yaml` declares a `project.activate` trigger. Council members run with context-asymmetric framing (see `core/VERIFICATION.md` §8.4). Each emits a `council.report`; convergence rule decides. Operator sees a single brief summary, not three free-form questions.
6. **Executes.** Operator runs `hw next-step` or invokes the first task. The first task's `consumes:` list typically references `OR-001` only; downstream tasks consume artifacts produced by earlier ones.

### Operator mid-flow directives

If the operator issues an instruction during bootstrap (or mid-task) that does not fit the schema's `bootstrap_questions` — e.g., "use the browser when needed", "Techsico IT and Techsico are separate companies", "treat anything from the 2025 audit as primary" — capture it as a typed Decision artifact, not as loose conversation.

The pattern:

1. The agent recognizes a directive that affects project structure or scope.
2. The agent drafts a Decision artifact body capturing the directive **verbatim** (or with explicit paraphrase markers — see Tier 1 verbatim quotation principle in `schemas/projects/<name>/rules-template.md`).
3. `hw add decision < draft.md` with an appropriate `synthesis_role` or schema-specific role (typical values: `scope-decision`, `weighting-rule`, `inclusion-exclusion`).
4. Subsequent tasks consume the new DEC by citation.

Loose-prose directives that affect project structure are unverifiable: they don't appear in `consumes:` lists, can't be cited, and disappear when the conversation context turns over. Typed Decisions are citable, hash-verified, regenerable, and survive session boundaries. The cost is one event per directive — under 30 seconds — and well within the substrate's everyday workload.

This applies during bootstrap (corrections to the first OR draft, web-research-policy directives, naming clarifications) and mid-execution (scope expansions, weight overrides, mid-flight constraint changes). The friction log entry A-12 motivates this convention.

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

Every command has a documented protocol in `core/SUBSTRATE.md`. The agent operates them by reading and writing files; no binary required.

---

## Per-Model Profiles

Different models respond differently to the same harness primitives. v5.0 ships profiles for the major frontier models so harness behavior adapts declaratively. See `templates/models/README.md` for the field reference and the override-precedence rules. The active profile is selected at scaffold time and frozen into `.hyperworker/models/`.

Profiles document what each model does *differently*, not which is "better." Where a model's behavior is documented in a postmortem (e.g., Anthropic's 2026-04-23 4.7 postmortem on suppress-concise-directives), the profile cites it. Operators add profiles over time; the directory is a library, not a fixed set.

---

## Startup Validation

Before delegating any task, the agent confirms:

- `HARNESS.md`, `core/SUBSTRATE.md` readable.
- `.hyperworker/events.jsonl` exists (or is empty for a fresh init).
- `.hyperworker/config.yaml` declares an active model profile.
- `projects/active_project.md` resolves to a project with `PROJECT.md`, `00-REFERENCE-rules.md`, and at least one task.
- `hw verify` returns `OK` (or, on a fresh project, an empty-log `OK`).

If any check fails, STOP. Report what is missing. The operator resolves before execution begins.

---

## Core Principles

1. **Substrate over rules.** Every primitive that survives is one verifiable without asking the agent if it complied.
2. **Heavy upfront, light ongoing.** Setup carries the cost; runtime is autonomous.
3. **Append-only events; regenerable projections.** Knowledge is not "managed" via lifecycles; it is recorded and superseded.
4. **Five mechanisms plus substrate.** No sixth mechanism without a falsifiable hypothesis and a structural check.
5. **Theory, not finding.** Each primitive is a hypothesis (see `core/*.md` §Hypothesis sections). v5.1 retires whatever fails its falsifier in real use.
