# Mechanism: Lock — Single-Project Focus

> **Audit trace:** A1, B1, B2, B4, B8, G1, G2, G3

## The Problem It Solves

AI models are eager to help with everything simultaneously. A user with twenty ideas and one AI assistant will end up with twenty half-built things and zero shipped deliverables. The Lock mechanism enforces a single active project at any time. All other ideas are captured but not executed.

## How It Works

### The Active Project Pointer

`active_project.md` is a lightweight pointer file. It contains only the name and path of the currently active project. The actual project definition lives in its own folder under `projects/`.

```markdown
# Active Project

**Current:** [Project Name]
**Path:** projects/[project-name]/PROJECT.md
**Started:** [YYYY-MM-DD]
**Status:** IN PROGRESS

## Quick Context
[One-line summary of where the project stands]
```

The architecture supports multiple project folders existing simultaneously. Only one holds the "active" flag. Switching projects is a deliberate act — update the pointer, not rebuild the world.

### The Backlog

`backlog.md` captures every idea that is NOT the active project. Each idea is synthesized into a one-paragraph entry and appended with a priority tag (HIGH / MEDIUM / LOW), grouped by theme.

**The critical rule:** Nothing in the backlog gets executed. The AI acknowledges new ideas, logs them, and returns focus to the active project.

### The Project Archive

Completed project folders are moved to `projects/archive/`. This preserves the full history (tasks, post-mortems, discoveries) while clearing the active workspace.

## The Distraction Blocking Protocol

When the operator provides a new idea unrelated to the active project:

1. **Acknowledge** — Validate the idea. Show it was heard.
2. **Synthesize** — Distill to a backlog-ready entry.
3. **Append** — Add to `backlog.md` with a priority tag.
4. **Do NOT execute** — No building, no deep-diving, no "let me just sketch this out."
5. **Redirect** — "This is logged. Back to [Active Project] — where were we?"

If the operator pushes to work on the new idea: *"Are we officially shelving [Active Project] to promote [New Idea] to the active slot, or should I just log this in the backlog?"*

This question forces a deliberate decision. Unconscious project-switching is the primary enemy of shipped work.

## The Project Completion Protocol

When the active project reaches 100% completion:

1. **Discovery sweep** — Read all Post-Task Discovery Capture sections from `done/` files. Add any undocumented discoveries to DISCOVERIES.md.
2. **Final review** — Check all deliverables against completion criteria. Verify no constraint violations.
3. **Learning promotion** — Review DISCOVERIES.md. Promote validated discoveries to LEARNINGS.md with lifecycle fields and scope tags.
4. **Version control commit** — Commit all changes to the project's repository (tool and workflow are configurable — see `config-skeleton.yaml`).
5. **Archive** — Move the project folder to `projects/archive/`. Clear the `active_project.md` pointer.
6. **Present the top 3** — Read `backlog.md` and present the three highest-priority items for selection.
7. **Deliberate selection** — The human picks the next project. A new project folder is created. The cycle begins again.

## When to Use Lock

Lock is always on. There is no scenario in this system where two projects are simultaneously active. If parallel workstreams are needed, each gets its own harness instance.

## Relationship to Other Mechanisms

- **Atomicity** decomposes the locked project into executable units.
- **Dependency** tracks the execution order within the locked project.
- **Memory Pipeline** captures knowledge that persists after the locked project completes.
- **Precedence** resolves rule conflicts within the locked project.
