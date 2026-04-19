# Mechanism: Dependency — Task State Engine


## The Problem It Solves

When task dependencies are invisible, downstream tasks proceed on stale assumptions. Task 5 assumes Task 3's output, but Task 3 failed silently — Task 5 runs anyway and produces wrong output. The Dependency mechanism makes all prerequisites explicit and prevents invalid execution order.

## How It Works

### TASK-STATE.yaml

A lightweight dependency graph and status tracker that lives in each project folder. It is the single source of truth for what can run, what's blocked, and what's done.

```yaml
# TASK-STATE.yaml — [Project Name]
# Updated: YYYY-MM-DD
#
# The planner updates this file. Executors reference it (read-only).
# Status values: pending | in_progress | complete | blocked | failed

project: "[project-name]"

phases:
  1:
    name: "[Phase Name]"
    checkpoint: null    # null = no gate. String = pause description.
    tasks:
      - id: "01"
        title: "[Task title]"
        status: pending
        depends_on: []
        assumptions:
          - "[What must be true for this task to succeed]"
        output_hash: null         # Optional: short hash for change detection
        completed_date: null
        discoveries: 0

      - id: "02"
        title: "[Task title]"
        status: pending
        depends_on: ["01"]
        assumptions:
          - "[Assumption — if invalidated, this task is flagged]"
        output_hash: null
        completed_date: null
        discoveries: 0

  2:
    name: "[Phase Name]"
    checkpoint: "PAUSE — [Human action required before this phase begins]"
    tasks:
      - id: "03"
        title: "[Task title]"
        status: pending
        depends_on: ["01", "02"]
        assumptions:
          - "[Assumption]"
        output_hash: null
        completed_date: null
        discoveries: 0
```

### Task Statuses

Five states cover the full lifecycle:

| Status | Meaning |
|---|---|
| `pending` | Not yet started. Dependencies may or may not be met. |
| `in_progress` | Currently being executed by an executor. |
| `complete` | Finished and verified. Output is stable. |
| `blocked` | Cannot proceed — missing dependency, failed assumption, or conflicting instructions. |
| `failed` | Attempted and did not produce valid output. Requires planner intervention. |

### The State Engine Protocol

**Before starting a task:**
1. Check that ALL `depends_on` tasks are `complete`.
2. Check that the phase checkpoint (if any) has been cleared by the human.
3. Check that no assumptions have been recently invalidated.

**After a task completes:**
1. Update status to `complete`.
2. Set `completed_date`.
3. Set `output_hash` (optional but recommended for complex dependency chains).
4. Record discovery count.
5. If discoveries > 0, review Post-Task Discovery Capture in the task file.

**When an assumption is invalidated:**
1. Search ALL tasks for that assumption — including tasks already marked `complete`.
2. Flag affected tasks for re-review.
3. Update or add the corrected assumption.
4. Document the change in DISCOVERIES.md.

### YAML Frontmatter in Task Files

Every task file declares its own dependencies and assumptions in YAML frontmatter. This is the local copy — TASK-STATE.yaml is the global tracker.

```yaml
---
task_id: "03"
title: "[Task title]"
depends_on: ["01", "02"]
assumptions:
  - "[Assumption 1]"
  - "[Assumption 2]"
phase: 2
status: pending
---
```

Executors check this frontmatter before executing. If a dependency isn't met or an assumption appears false, the executor STOPS and reports.

### Phase Checkpoints

Phases create explicit gates between major stages of work. A checkpoint is a string that describes what the human must do before the next phase begins. When the system reaches a checkpoint, it pauses and waits.

Checkpoints can be human gates (manual approval) or automated gates (a CI check, a test suite) depending on the domain. The mechanism is the same — execution halts until the gate clears.

The frequency of checkpoints is configurable. Regulated domains may need a gate after every phase. Rapid-iteration domains may only gate at major milestones.

### Output Hashes

An optional lightweight integrity mechanism. When a task completes, the planner records a short hash of its key output. If that output is later modified, downstream tasks that depend on it can be flagged for re-review.

Output hashes are recommended for projects with complex dependency chains where outputs are referenced by multiple downstream tasks. They can be omitted for simple linear projects.

## Relationship to Other Mechanisms

- **Lock** determines which project's dependency graph is active.
- **Atomicity** defines the individual tasks that the dependency graph connects.
- **Memory Pipeline** captures discoveries from tasks, which may invalidate assumptions in the graph.
- **Precedence** resolves conflicts that surface when dependencies clash with rules.
