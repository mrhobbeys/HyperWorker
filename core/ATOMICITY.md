# Mechanism: Atomicity — One Task Per File, One File Per Session


## The Problem It Solves

AI models suffer from context degradation. In long sessions, early instructions get compressed or forgotten, and the AI drifts from the original scope. Monolithic task instructions reliably fail after approximately the fifth step. Atomicity decomposes every project into individually numbered task files, each designed to be completed in a single AI session without drift.

## How It Works

### The Atomic Task File

Every task file is self-contained, single-session-sized, explicitly bounded, and verifiable. See `templates/task-template.md` for the complete format. Key fields: `task_id`, `depends_on`, `assumptions`, `phase`, `status`, `risk_level`.

### Key Design Principles

- **Explicit over implicit.** Not "update the headline" but "go to this URL, click the pencil icon, edit the Headline field, paste this exact text, save."
- **One field, one row.** For tasks that touch UI fields, the Field-Value Map is the authoritative spec. A single field's value never appears in more than one row or more than one step. Step-by-step instructions describe navigation; the Field-Value Map describes destination state.
- **Boundaries stated as positives AND negatives.** "What To Do" defines positive scope. "Do NOT Touch" defines negative scope. Both required.
- **Verification is mandatory.** The checklist + evidence trail is the definition of "done." No task is complete until every item is confirmed and evidence recorded.
- **Discovery capture is baked in.** Every task includes a section for the executor to note unexpected findings. This feeds the Memory Pipeline without giving the executor permission to act on discoveries.

### Content Delivery Modes

| Mode | Who Writes | When to Use |
|---|---|---|
| **Execute pre-authored** | Planner writes content during planning; executor pastes it exactly | Regulated, legal-sensitive, or brand-critical work |
| **Generate within constraints** | Executor generates content within specified boundaries | Creative, exploratory, or technical documentation work |
| **Iterate within boundaries** | Executor produces multiple candidates, operator selects or redirects, executor refines until convergence | Visual assets, copy exploration, design work where first-pass fidelity is impossible |

The mode is declared per task. All three are valid.

When mode is "Iterate within boundaries," the task file must include:
- **Preview surface** — a live URL, screenshot, or preview environment the executor loads before producing output, so constraints (safe areas, character counts, rendering) are measured against reality, not assumed.
- **Version preservation** — each pass saves to a new filename (`banner-v1.png`, `banner-v2.png`). Earlier versions are never overwritten.
- **Convergence criterion** — an explicit condition under which iteration stops ("operator approves," "matches reference within N pixels," "three passes maximum, then STOP and escalate").

The executor still STOPs when convergence is reached. Iteration is bounded, not open-ended.

### The `done/` Folder

Completed task files are moved to `done/`. This serves three purposes:

1. **Progress visibility** — `ls tasks/` shows remaining work. `ls done/` shows completed work.
2. **Audit trail** — The original task file shows what was supposed to happen.
3. **Post-mortem capture** — If a task produced a discovery, the Post-Task Discovery Capture section is filled in before the file moves to `done/`.

### Session State — Step-Level Resume

Tasks can span sessions. A session may end mid-task from context compaction, crash, power loss, operator interruption, or planned agent handoff. TASK-STATE.yaml is task-level; it does not record which step has completed. Session State fills that gap.

One file per project: `projects/[project-name]/SESSION-STATE.md`. Overwritten on every numbered step completion. Records active task, step number, last action, reference to the most recent Evidence Trail row, and next action. Does not duplicate Evidence Trail or task file content — it is a pointer to state held elsewhere.

**Check-in cadence:** the executor writes SESSION-STATE.md after every numbered step in Step-by-Step Instructions. This is the atomic check-in unit — smaller than a task, larger than a single tool call.

**Resume protocol:** on starting, read SESSION-STATE.md before the task file. If Status is `in_progress` for the requested task, resume at the first incomplete step. Otherwise begin at step 1.

**Relationship to TASK-STATE.yaml:** TASK-STATE is task-level and tracks all tasks in the project. SESSION-STATE is step-level and tracks at most one task at a time. The executor writes SESSION-STATE throughout step execution and performs a final write at task completion that sets Status `ready` and Active task `none`. The planner writes SESSION-STATE when assigning the next task, pointing Active task at the new task before the executor begins.

**Out of scope:** action-level state (every tool call, browser URL, modal state). That level would require a database and break the "files as source of truth" principle. If step-level resume is insufficient for a task, decompose the task further rather than escalating state tracking.

### The Executor Prompt

Every executor session starts by loading a behavioral prompt that enforces atomicity. The core rules:

1. Do ONLY what the task file says. Nothing more.
2. Do NOT look ahead to other tasks or suggest next steps.
3. Do NOT edit anything marked "Do NOT Touch."
4. Do NOT create new content unless explicitly asked.
5. When given content to deliver, deliver it EXACTLY. Do not rewrite "for consistency."
6. After completing the task, verify against the checklist. Report what changed.
7. When done, STOP.

Additional rules enforce escalation (see Precedence) and discovery capture (see Memory Pipeline).

### The Escalation Protocol

When an executor hits something it cannot resolve — conflicting constraints, blocked dependency, ambiguous instruction:

1. **STOP.** Do not attempt to resolve.
2. **Document** the conflict in Post-Task Discovery Capture.
3. **Set task status to `blocked`.**
4. **Report** the specific conflict and the clashing rules/assumptions.

Being blocked is a valid and expected outcome, not a failure. The planner resolves the conflict and the executor resumes.

For the proactive counterpart (flagging problems *before* execution begins), see the Pushback Protocol in `core/VERIFICATION.md`.

## Relationship to Other Mechanisms

- **Lock** determines which project is being decomposed.
- **Dependency** tracks execution order between atomic tasks.
- **Memory Pipeline** captures knowledge from completed tasks.
- **Precedence** resolves rule conflicts the executor encounters during execution.
