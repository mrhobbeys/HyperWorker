# Mechanism: Atomicity — One Task Per File, One File Per Session


## The Problem It Solves

AI models suffer from context degradation. In long sessions, early instructions get compressed or forgotten, and the AI drifts from the original scope. Monolithic task instructions reliably fail after approximately the fifth step. Atomicity decomposes every project into individually numbered task files, each designed to be completed in a single AI session without drift.

## How It Works

### The Atomic Task File

Every task file is self-contained, single-session-sized, explicitly bounded, and verifiable. See `templates/task-template.md` for the complete format. Key fields: `task_id`, `depends_on`, `assumptions`, `phase`, `status`, `risk_level`.

### Key Design Principles

- **Explicit over implicit.** Not "update the headline" but "go to this URL, click the pencil icon, edit the Headline field, paste this exact text, save."
- **Boundaries stated as positives AND negatives.** "What To Do" defines positive scope. "Do NOT Touch" defines negative scope. Both required.
- **Verification is mandatory.** The checklist + evidence trail is the definition of "done." No task is complete until every item is confirmed and evidence recorded.
- **Discovery capture is baked in.** Every task includes a section for the executor to note unexpected findings. This feeds the Memory Pipeline without giving the executor permission to act on discoveries.

### Content Delivery Modes

| Mode | Who Writes | When to Use |
|---|---|---|
| **Execute pre-authored** | Planner writes content during planning; executor pastes it exactly | Regulated, legal-sensitive, or brand-critical work |
| **Generate within constraints** | Executor generates content within specified boundaries | Creative, exploratory, or technical documentation work |

The mode is declared per task. Both are valid.

### The `done/` Folder

Completed task files are moved to `done/`. This serves three purposes:

1. **Progress visibility** — `ls tasks/` shows remaining work. `ls done/` shows completed work.
2. **Audit trail** — The original task file shows what was supposed to happen.
3. **Post-mortem capture** — If a task produced a discovery, the Post-Task Discovery Capture section is filled in before the file moves to `done/`.

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
