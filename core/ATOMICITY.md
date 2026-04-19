# Mechanism: Atomicity — One Task Per File, One File Per Session

> **Audit trace:** A2, B3, C1, C8-C10, E1-E2, E6, E8

## The Problem It Solves

AI models suffer from context degradation. In long sessions, early instructions get compressed or forgotten, and the AI drifts from the original scope. Monolithic task instructions reliably fail after approximately the fifth step. Atomicity decomposes every project into individually numbered task files, each designed to be completed in a single AI session without drift.

## How It Works

### The Atomic Task File

Every task file is self-contained, single-session-sized, explicitly bounded, and verifiable. The anatomy:

```markdown
---
task_id: "[ID]"
title: "[Descriptive Task Name]"
depends_on: []
assumptions:
  - "[What must be true for this task to succeed]"
phase: [N]
status: pending
---

# Task [ID]: [Descriptive Task Name]

**Read `00-REFERENCE-rules.md` first.**

## What To Do
[One paragraph stating the exact objective. Be specific about the end state.]

## Step-by-Step Instructions
[Detailed, numbered steps. Exact text to paste, fields to fill, buttons to click.]

## CRITICAL — [Domain-Relevant Check]
[A mandatory check relevant to the project. Examples:]
[- Scan all text for Tier 1 violations from the reference file]
[- Verify all URLs resolve correctly]
[- Confirm output meets platform constraints]

## Do NOT Touch
[Explicit list of things the worker must leave alone]

## Verification Checklist
- [ ] [Specific deliverable confirmed]
- [ ] Zero violations of reference rules (Tier 1 checked first)
- [ ] No unintended changes to out-of-scope areas
- [ ] STOP HERE — do not proceed to next task

## Post-Task Discovery Capture
[See Memory Pipeline mechanism]
```

### Key Design Principles

**Explicit over implicit.** The task file doesn't say "update the headline." It says: "Go to this URL. Click the pencil icon. Edit the Headline field. Paste this exact text. Save."

**Boundaries are stated as positives AND negatives.** "What To Do" defines the positive scope. "Do NOT Touch" defines the negative scope. Both are required.

**Verification is mandatory.** The checklist at the end is the definition of "done." No task is complete until every checkbox is confirmed.

**Discovery capture is baked in.** Every task includes a section for the worker to note unexpected findings. This feeds the Memory Pipeline without giving the worker permission to act autonomously on discoveries.

### Content Delivery Modes

Tasks can operate in two modes depending on the project type:

**Execute pre-authored** — The exact content to deliver is pre-written during planning. The worker pastes it, doesn't write it. Writing happened during the orchestrator planning phase. This is the default for regulated, legal-sensitive, or brand-critical work.

**Generate within constraints** — The task specifies the objective, constraints, and style parameters, and the worker generates content within those boundaries. This mode is appropriate for creative, exploratory, or technical documentation work where the orchestrator cannot pre-author every deliverable.

The mode is declared per task. Both are valid.

### The `done/` Folder

Completed task files are moved to `done/`. This serves three purposes:

1. **Progress visibility** — `ls tasks/` shows remaining work. `ls done/` shows completed work.
2. **Audit trail** — The original task file shows what was supposed to happen.
3. **Post-mortem capture** — If a task produced a discovery, the Post-Task Discovery Capture section is filled in before the file moves to `done/`.

### The Worker Prompt

Every worker session starts by loading a behavioral prompt that enforces atomicity. The core rules:

1. Do ONLY what the task file says. Nothing more.
2. Do NOT look ahead to other tasks or suggest next steps.
3. Do NOT edit anything marked "Do NOT Touch."
4. Do NOT create new content unless explicitly asked.
5. When given content to deliver, deliver it EXACTLY. Do not rewrite "for consistency."
6. After completing the task, verify against the checklist. Report what changed.
7. When done, STOP.

Additional rules enforce escalation (see Precedence) and discovery capture (see Memory Pipeline).

### The Escalation Protocol

When a worker hits something it cannot resolve — conflicting constraints, blocked dependency, ambiguous instruction:

1. **STOP.** Do not attempt to resolve.
2. **Document** the conflict in Post-Task Discovery Capture.
3. **Set task status to `blocked`.**
4. **Report** the specific conflict and the clashing rules/assumptions.

Being blocked is a valid and expected outcome, not a failure. The orchestrator resolves the conflict and the worker resumes.

## Relationship to Other Mechanisms

- **Lock** determines which project is being decomposed.
- **Dependency** tracks execution order between atomic tasks.
- **Memory Pipeline** captures knowledge from completed tasks.
- **Precedence** resolves rule conflicts the worker encounters during execution.
