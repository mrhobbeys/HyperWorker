# Quick Start — Focus & Execution Harness v3.1

## What Is This?

A project management system for AI-assisted delivery. It keeps you focused on one project at a time, breaks work into small executable tasks, tracks what depends on what, remembers what you learn, and resolves rule conflicts automatically.

## First Time Setup

1. **Read `HARNESS.manifest`** in the root folder. This tells you (and the AI) which files are the system and which are your project.

2. **Copy `templates/config-skeleton.yaml`** to the root as `config.yaml`. Fill in your settings — at minimum, set the AI models you're using and your platform.

3. **Tell the AI what you want to accomplish.** Describe your project. The AI will ask you questions, then scaffold your project files from the templates.

4. **Review the scaffold.** The AI will pause and ask you to confirm three things: your project description, your priority rules, and your task breakdown. Fix anything that's wrong before proceeding.

5. **Start working.** Say "next step" to get your first task.

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
├── HARNESS.manifest     ← Read this first
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
