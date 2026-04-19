# Quick Start — HyperWorker v4.0

## What Is This?

A project management harness for AI agents. It keeps you focused on one project at a time, breaks work into small executable tasks, tracks dependencies, remembers what you learn, resolves rule conflicts automatically, and proves completion with evidence.

## First Time Setup

1. **Point any AI agent at this repository.**

2. **Say:** "Read `HARNESS.md` and build me a harness for [describe your goal]."

The agent reads HARNESS.md, asks you clarifying questions, scaffolds project files from the templates, runs a verification checkpoint (confirming your project description, rules, and task breakdown), and begins execution. No config to copy manually — the agent handles it.

3. **Start working.** Say "next step" to get your first task.

## Day-to-Day Commands

| Say This | What Happens |
|---|---|
| "Next step" | AI finds your next task and tells you what to do |
| "Status check" | AI reports what's done, pending, and blocked |
| "Log this" | AI saves your idea to the backlog without starting work on it |
| "Park this" | AI shelves the current project so you can switch |
| "Wrap it up" | AI runs the completion protocol and presents the next project options |

## Optional: Domain Research

If you want the AI to research your domain before scaffolding (to pre-populate config values and rules), set `research.enabled: true` in `config.yaml`. This adds 3-5 minutes to setup but can improve the initial scaffold for unfamiliar domains. See `reference/RESEARCH-PROTOCOL.md` for details.

## Key Concepts

**One project at a time.** Everything else goes on the backlog.

**One task per session.** Each task is small enough to finish without the AI losing track.

**Rules have ranks.** When rules conflict, higher-ranked rules win. No guessing.

**Discoveries become knowledge.** When something unexpected happens, it gets captured. You decide if it becomes a permanent rule.

## Folder Structure

```
harness/
├── HARNESS.md           ← Read this first
├── config.yaml          ← Your settings
├── core/                ← System docs (don't modify during projects)
├── templates/           ← Starting points for project files
├── reference/           ← Guides and known limitations
├── starter/             ← You are here
├── projects/            ← Your actual work goes here
├── backlog.md           ← Ideas waiting their turn
└── memory/              ← What you've learned across projects
```

## Need Help?

- **Something broke?** Check `reference/FAILURE-MODES.md` — your issue might be a known limitation.
- **New domain?** Use `reference/VALIDATION.md` to test if the harness fits.
- **Want to research first?** See `reference/RESEARCH-PROTOCOL.md`.
