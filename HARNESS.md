# HyperWorker v4.0

A project management harness for AI agents. Six mechanisms enforced through markdown and YAML files make long-running projects survive agent context loss, scope drift, skipped steps, rule conflicts, knowledge decay, and unverified claims of completion.

**Read this file first. It is the single entry point for the entire system.**

---

## Quick Start

1. Point any AI agent at this repository.
2. Say: **"Read HARNESS.md and build me a harness for [describe your goal]."**

The agent reads this file, asks clarifying questions, scaffolds project files from the templates, runs the Verification Checkpoint, and begins execution. No prerequisites, no config to copy first — the agent handles setup.

---

## The Six Mechanisms

Each mechanism solves a specific failure mode. Together they form a closed system where focus is enforced, work is decomposed, dependencies are tracked, knowledge compounds, rules don't conflict, and completion is proven.

| Mechanism | What It Solves | Core File |
|---|---|---|
| **Lock** | Drift — too many projects in flight | [core/LOCK.md](core/LOCK.md) |
| **Atomicity** | Context loss — AI forgets in long sessions | [core/ATOMICITY.md](core/ATOMICITY.md) |
| **Dependency** | Skipped steps — tasks run on stale assumptions | [core/DEPENDENCY.md](core/DEPENDENCY.md) |
| **Memory** | Knowledge loss — discoveries never become knowledge | [core/MEMORY.md](core/MEMORY.md) |
| **Precedence** | Rule conflicts — contradictory constraints, no resolution | [core/PRECEDENCE.md](core/PRECEDENCE.md) |
| **Verification** | Unproven work — tasks marked done without evidence | [core/VERIFICATION.md](core/VERIFICATION.md) |

---

## How It Works

The harness is a file-system contract. State lives in markdown and YAML files, not in memory, not in a database, not in a platform. Any AI that can read files and follow instructions can operate the harness. Sessions can crash, context can compact, models can change — the filesystem is the source of truth.

**Two roles, one principle:** Planning and execution are separate concerns. A **Planner** decomposes goals into tasks, authors reference documents, manages memory, and reviews quality. An **Executor** picks up one task file at a time, follows instructions, runs verification, captures discoveries, and stops.

**How the roles map to your platform:**
- **Subagent-capable platforms** (Claude Code, Goose): The planner spawns executor subagents for individual tasks.
- **Single-agent platforms** (Claude.ai, Cursor, Copilot): The same agent switches between planner and executor modes. The executor prompt in `templates/executor-prompt.md` enforces the behavioral boundary.
- **Two-model setups**: The most capable model plans. A fast, reliable model executes.

The mechanism is adaptive. The principle — separate planning from execution — is fixed.

---

## Routing Table

When performing an operation, read only the files listed for your role. This prevents wasting tokens on irrelevant content.

| Operation | Role | Read These Files |
|---|---|---|
| **Scaffolding a new project** | Planner | HARNESS.md → templates/config-skeleton.yaml, templates/project.md, templates/task.md, templates/rules.md |
| **Executing a task** | Executor | Project's 00-REFERENCE-rules.md → the specific task file → templates/executor-prompt.md |
| **Reviewing completed work** | Planner | TASK-STATE.yaml → completed task files in done/ → core/VERIFICATION.md (criteria only) |
| **Resuming a project (context recovery)** | Planner | active_project.md → PROJECT.md → TASK-STATE.yaml → 00-REFERENCE-rules.md |
| **Resolving a blocked task** | Planner | task file → TASK-STATE.yaml → relevant core/*.md |
| **Managing memory** | Planner | core/MEMORY.md → memory/DISCOVERIES.md → memory/LEARNINGS.md |
| **Resolving rule conflicts** | Planner | core/PRECEDENCE.md → project's 00-REFERENCE-rules.md |
| **Verifying completion** | Executor | Task's verification checklist → evidence trail (both within the task file) |
| **Understanding a mechanism** | Either | The specific core/*.md file for that mechanism |
| **Validating in a new domain** | Planner | reference/VALIDATION.md → templates/ → case-studies/ |

---

## Truth Layer vs Mutable Surface

The harness draws a hard boundary between infrastructure and project content. The AI must never confuse the two.

### Truth Layer — Harness Infrastructure

These files define HOW work is managed. Never modify them during project execution.

```
core/
├── LOCK.md                  # Single-project focus mechanism
├── ATOMICITY.md             # One task per file, one file per session
├── DEPENDENCY.md            # Task state engine and dependency tracking
├── MEMORY.md                # Discovery-to-learning lifecycle
├── PRECEDENCE.md            # Tiered rule resolution
└── VERIFICATION.md          # Evidence-based completion

templates/
├── config-skeleton.yaml     # Configurable system parameters
├── executor-prompt.md       # Behavioral rules for executor sessions
├── task.md                  # Task file starting point
├── project.md               # Project definition starting point
├── rules.md                 # Precedence rules starting point
└── post-mortem.md           # Post-task review starting point

reference/
├── VALIDATION.md            # Domain validation guide
├── FAILURE-MODES.md         # Known limitations and edge cases
└── RESEARCH-PROTOCOL.md     # Optional domain research protocol

case-studies/                # Worked examples across five domains
starter/README.md            # Quick-start guide

HARNESS.md                   # This file — system entry point
CHANGELOG.md                 # Version history
VISION.md                    # Architectural constitution
README.md                    # Project description
CONTRIBUTING.md              # Contribution guidelines
LICENSE                      # MIT
```

### Mutable Surface — Project Content

These files ARE the work being managed. Created from templates when a project starts.

```
projects/
├── active_project.md              # Pointer to current active project
├── [project-name]/
│   ├── PROJECT.md                 # Objective, scope, constraints
│   ├── TASK-STATE.yaml            # Dependency graph and status tracker
│   ├── 00-REFERENCE-rules.md      # Cross-cutting rules with precedence tiers
│   ├── EXECUTOR-PROMPT.md         # Project-specific executor behavioral rules
│   ├── tasks/                     # Active task pipeline
│   └── done/                      # Completed tasks with post-mortem notes
├── archive/                       # Completed project folders

backlog.md                         # All non-active ideas, prioritized
config.yaml                        # Deployment-specific settings

memory/
├── DISCOVERIES.md                 # Raw findings awaiting human validation
├── LEARNINGS.md                   # Validated knowledge with lifecycle fields
└── LEARNINGS-ARCHIVE.md           # Aged entries, searchable but off critical path
```

### Boundary Rule

If unsure whether a file is harness or project content: if it's listed under Truth Layer, it defines HOW work is managed — don't touch it during execution. If it's listed under Mutable Surface or not listed at all, it IS the work being managed.

---

## Bootstrap Protocol

When an AI agent reads this file and is asked to build a harness for a goal, follow this sequence:

### 1. Understand the Goal
Ask the operator:
- What is the project? What does "done" look like?
- What domain is this in? What are the key constraints?
- Are there existing rules, brand guidelines, or compliance requirements?

Optional: If the operator wants domain research before scaffolding, see `reference/RESEARCH-PROTOCOL.md`.

### 2. Scaffold Project Files
Using the templates, create:
- `config.yaml` from `templates/config-skeleton.yaml` — fill in based on answers
- `projects/[project-name]/PROJECT.md` from `templates/project.md`
- `projects/[project-name]/00-REFERENCE-rules.md` from `templates/rules.md`
- `projects/[project-name]/TASK-STATE.yaml` — decompose goal into tasks with dependencies
- `projects/[project-name]/tasks/*.md` from `templates/task.md` — one file per task
- `projects/[project-name]/EXECUTOR-PROMPT.md` from `templates/executor-prompt.md`
- `projects/active_project.md` — pointer to the new project
- `memory/DISCOVERIES.md`, `memory/LEARNINGS.md` — empty files ready for use

### 3. Verification Checkpoint (Mandatory)
Before any task execution begins, pause and present three questions:

1. **"Does this project description match your intent?"** — Show PROJECT.md objective and scope.
2. **"Do these priority tiers make sense for your domain?"** — Show 00-REFERENCE-rules.md tier names and example rules.
3. **"Does this task breakdown look right?"** — Show TASK-STATE.yaml task list with dependencies.

The operator confirms or corrects each. No task execution begins until all three are confirmed. This checkpoint is mandatory for new projects. It is not required when resuming existing projects.

### 4. Execute
Work through tasks one at a time using the Standard Commands below.

---

## Standard Commands

| Command | Behavior |
|---|---|
| **"Next step"** | Read TASK-STATE.yaml. Find next pending task with all dependencies met. Report what to do. |
| **"Status check"** | Read TASK-STATE.yaml. Report: complete, pending, blocked, discoveries awaiting review. |
| **"Log this"** | Intake only. Synthesize and append to backlog. Do not execute. |
| **"Wrap it up"** | Initiate completion protocol: discovery sweep → review → promote learnings → commit → archive → present backlog. |
| **"Review discoveries"** | Present each Open entry in DISCOVERIES.md for validation. Promote or archive. |
| **"Learning sweep"** | Flag DEPRECATED entries in LEARNINGS.md. Present for re-validation or archival. |
| **"Park this"** | Demote active project to backlog. Clear pointer. |

Commands are extensible. Add domain-specific commands to the project's EXECUTOR-PROMPT.md.

---

## Startup Validation

Before executing any task, the planner must verify:

- HARNESS.md exists and is readable.
- config.yaml exists and all required fields are populated.
- projects/active_project.md points to a valid project folder.
- The active project has: PROJECT.md, TASK-STATE.yaml, 00-REFERENCE-rules.md.
- At least one task file exists in the active project's tasks/ folder.

If any check fails, STOP. Do not proceed. Report what is missing. The operator must resolve structural issues before execution begins.

---

## Core Principles

1. **One active project at a time.** Everything else is backlog.
2. **Decompose to single-session tasks.** If it can't be done in one session without drift, it's too big.
3. **State boundaries explicitly.** What to do, what not to touch, what "done" looks like.
4. **Track dependencies, not just sequence.** Tasks declare what they need. The state engine prevents invalid execution.
5. **Separate planning from execution.** The planner plans. The executor executes. The mechanism adapts to your platform.
6. **Capture everything, execute deliberately.** Every idea gets logged. Nothing executes without being the active project.
7. **Let memory compound — but validate it.** Discoveries go through a human gate before becoming knowledge.
8. **Scope memory to prevent contamination.** One context's lessons don't silently infect another.
9. **Build for forgetting.** Memory without decay becomes noise.
10. **Enforce the stop.** When done, STOP. When blocked, STOP. Don't guess, don't expand.
11. **Verify before executing.** New projects require human confirmation of scope, rules, and task breakdown.
12. **Prove completion, don't claim it.** Evidence over assertion. Baseline-after comparison over "looks good."
