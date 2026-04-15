# The Focus & Execution Harness v3.1 — Core System

> **Read `HARNESS.manifest` before this file.** The manifest declares which files are harness infrastructure and which are project content. This distinction matters — the harness manages work, it is not the work itself.

## What This Is

A reusable project management and execution system for AI-assisted delivery. The harness solves two problems that get worse as AI models get more capable: they help with everything at once (producing twenty half-built things and zero shipped deliverables), and they lose context over long sessions (early instructions get compressed or forgotten).

The system is domain-agnostic. Swap in any goal — software, marketing, compliance, operations — and the harness works the same way.

## The Five Core Mechanisms

The harness is built on five mechanisms. Each solves a specific failure mode. Together they form a closed system where focus is enforced, work is decomposed, dependencies are tracked, knowledge compounds, and rules don't conflict.

| Mechanism | What It Solves | Core File |
|---|---|---|
| **Lock** | Diffusion — too many projects in flight | [/core/lock/](lock/LOCK.md) |
| **Atomicity** | Drift — AI loses context in long sessions | [/core/atomicity/](atomicity/ATOMICITY.md) |
| **Dependency** | Silent failures — tasks run on stale assumptions | [/core/dependency/](dependency/DEPENDENCY.md) |
| **Memory Pipeline** | Knowledge loss — discoveries never become operating knowledge | [/core/memory-pipeline/](memory-pipeline/MEMORY-PIPELINE.md) |
| **Precedence** | Rule conflicts — contradictory constraints with no resolution order | [/core/precedence/](precedence/PRECEDENCE.md) |

## System Architecture

```
harness/
├── HARNESS.manifest                   # READ FIRST — structural boundary declaration
├── CHANGELOG.md                       # Version history
├── core/                              # Mechanism documentation (you are here)
│   ├── SYSTEM.md
│   ├── lock/
│   ├── atomicity/
│   ├── dependency/
│   ├── memory-pipeline/
│   └── precedence/
├── projects/
│   ├── active_project.md              # Pointer to current active project
│   ├── [project-name]/                # Per-project folders
│   │   ├── PROJECT.md                 # Objective, scope, constraints, completion criteria
│   │   ├── TASK-STATE.yaml            # Dependency graph and status tracker
│   │   ├── 00-REFERENCE-rules.md      # Cross-cutting rules with precedence tiers
│   │   ├── WORKER-PROMPT.md           # Behavioral constraints for worker sessions
│   │   ├── tasks/                     # Active task pipeline
│   │   └── done/                      # Completed tasks with post-mortem notes
│   └── archive/                       # Completed project folders
├── backlog.md                         # All non-active ideas, prioritized
├── config.yaml                        # Deployment-specific settings (from config-skeleton)
├── memory/
│   ├── DISCOVERIES.md                 # Raw findings awaiting human validation
│   ├── LEARNINGS.md                   # Validated knowledge with lifecycle fields
│   └── LEARNINGS-ARCHIVE.md           # Aged entries, searchable but off critical path
├── templates/                         # Blank starting points for all file types
│   ├── config-skeleton.yaml           # Configurable system parameters
│   ├── worker-prompt-template.md
│   ├── task-template.md
│   ├── project-template.md
│   ├── rules-template.md
│   └── post-mortem-template.md
├── reference/
│   ├── VALIDATION.md                  # How to validate the harness in a new domain
│   ├── FAILURE-MODES.md               # Known limitations and edge cases
│   └── RESEARCH-PROTOCOL.md           # Optional domain research protocol
└── starter/
    └── README.md                      # Quick-start guide for new deployments
```

## Getting Started

New to the harness? Start here:

1. **Read `HARNESS.manifest`** — understand the boundary between harness and project.
2. **Copy `templates/config-skeleton.yaml` to `config.yaml`** — fill in your deployment settings.
3. **Tell the orchestrator about your project** — describe what you want to accomplish. The orchestrator will ask clarifying questions, then scaffold your project using the templates.
4. **Verify the scaffold** — the orchestrator will pause and ask you to confirm the project description, priority tiers, and task breakdown before any work begins.
5. **Execute** — work through tasks one at a time using the standard commands below.

Optional: If you want the orchestrator to research your domain before scaffolding, see `reference/RESEARCH-PROTOCOL.md`.

## The Two-Tier Execution Model

The harness separates planning from execution using capability-appropriate agents.

**Tier 1: Orchestrator** — The most capable available model. Handles project decomposition, task authoring, copy creation, reference document authoring, memory management, backlog curation, quality review, discovery validation, and dependency tracking.

**Tier 2: Worker** — A fast, reliable model that follows instructions without embellishing. Executes one task file at a time, follows step-by-step instructions, runs verification checklists, escalates conflicts, and captures discoveries.

The separation reduces cost, prevents drift, and creates natural quality checkpoints. The specific models used are a configuration choice (see `config-skeleton.yaml`).

> **Scaling boundary:** This system is designed for a solo operator (one human + AI). Multi-user teams would need task assignment and handoff patterns not yet defined. See [FAILURE-MODES.md](../reference/FAILURE-MODES.md).

## Standard Commands

| Command | Behavior |
|---|---|
| **"Log this"** | Intake only. Synthesize and append to backlog. Do not execute. |
| **"Next step"** | Read TASK-STATE.yaml. Find next pending task with all dependencies met. Report what to do. |
| **"Wrap it up"** | Initiate completion protocol: discovery sweep → review → promote learnings → commit → archive → present backlog. |
| **"Status check"** | Read TASK-STATE.yaml. Report: complete, pending, blocked, discoveries awaiting review. |
| **"Review discoveries"** | Present each Open entry in DISCOVERIES.md for validation. Promote or archive. |
| **"Learning sweep"** | Flag DEPRECATED entries in LEARNINGS.md. Present for re-validation or archival. |
| **"Park this"** | Demote active project to backlog. Clear pointer. |

Commands are extensible. Add domain-specific commands to the project's WORKER-PROMPT.md or the system prompt.

## The Verification Checkpoint

When the orchestrator scaffolds a new project, it must **pause before any task execution** and present three questions to the operator:

1. **"Does this project description match your intent?"** — Shows the PROJECT.md objective and scope.
2. **"Do these priority tiers make sense for your domain?"** — Shows the 00-REFERENCE-rules.md tier names and example rules.
3. **"Does this task breakdown look right?"** — Shows the TASK-STATE.yaml task list with dependencies.

The operator confirms or corrects each. This checkpoint prevents the failure mode where the AI proceeds with wrong assumptions about what the project is or how the domain works.

This checkpoint is mandatory for new projects. It is not required when resuming an existing project that has already been confirmed.

## The Version Evolution Principle

The system preserves its own history. Original documents are kept alongside revisions. Neither is deleted — v1 shows original thinking, v2 shows what changed and why, and the delta encodes decisions that would be lost if v1 were overwritten.

## Configuration

The harness ships with sensible defaults that can be overridden per deployment. All configurable parameters live in [`config-skeleton.yaml`](../templates/config-skeleton.yaml): AI model assignments, memory review cadence, scope tag taxonomy, precedence tier naming, and platform-specific settings.

## Core Principles

1. **One active project at a time.** Everything else is backlog.
2. **Decompose to single-session tasks.** If it can't be done in one AI session without drift, it's too big.
3. **State boundaries explicitly.** What to do, what not to touch, what "done" looks like.
4. **Track dependencies, not just sequence.** Tasks declare what they need. The state engine prevents invalid execution.
5. **Separate planning from execution.** The best model plans. A fast model executes.
6. **Capture everything, execute deliberately.** Every idea gets logged. Nothing executes without being the active project.
7. **Let memory compound — but validate it.** Discoveries go through a human gate before becoming knowledge.
8. **Scope memory to prevent contamination.** One context's lessons don't silently infect another.
9. **Build for forgetting.** Memory without decay becomes noise.
10. **Enforce the stop.** When done, STOP. When blocked, STOP. Don't guess, don't expand.
11. **Verify before executing.** New projects require human confirmation of scope, rules, and task breakdown before any work begins.
