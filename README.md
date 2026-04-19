![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Version: 4.0](https://img.shields.io/badge/Version-4.0-blue.svg)

# HyperWorker

**Project management harness for AI agents.**

Your AI agent starts strong — then forgets the plan, invents new scope, and breaks things it shouldn't touch. HyperWorker stops that.

HyperWorker is a repo of markdown and YAML — not a CLI, not a package, not a hosted service. It's a file-system contract that any AI agent reads and follows. Six enforced mechanisms keep long-running projects on track: no drift, no invented scope, no "mostly finished," no unproven claims of completion.

---

## The four things that break

If you've run a real project through an AI agent — not a one-shot task, but something with phases, dependencies, and work that spans multiple sessions — you've probably hit the wall:

1. **It drifts.** The agent invents scope, edits files outside its lane, or decides it knows better than the plan.
2. **It loses context between sessions.** Close the session, open it tomorrow, and the agent has no idea what happened yesterday.
3. **It skips steps.** No verification, no tracking — things get marked "done" that aren't done.
4. **There are no natural checkpoints.** You're reviewing constantly instead of at boundaries, because there are no boundaries.

HyperWorker was built to fix all four.

## How it works

Six mechanisms enforce the four things that were breaking:

**Lock** stops the drift. Only one project can be active at a time. Everything else goes on the backlog. Switching is a deliberate act, not a distraction.

**Atomicity** kills "mostly finished." Every task is a self-contained file designed for one AI session. Complete or not complete. No "90% done."

**Dependency** prevents skipped steps. Downstream tasks can't start until upstream tasks are verified. TASK-STATE.yaml tracks status, dependencies, and assumptions.

**Memory** solves the cross-session problem. What the agent learns gets scoped, tagged, and carried across sessions in the file system. Start a new session tomorrow, point the agent at `HARNESS.md`, and it knows exactly where you left off.

**Precedence** creates natural checkpoints. When rules conflict, tiered resolution decides. Your absolute rules always beat your style preferences. No guessing.

**Verification** proves completion. Tasks require evidence trails — not just checkmarks. Baseline-after comparison catches regressions. The ratchet principle: improvements kept, regressions discard the completion claim.

Plus a clear boundary declaration in `HARNESS.md` that separates the Truth Layer (harness infrastructure) from the Mutable Surface (project content), so the agent knows its boundaries before it touches anything.

## Getting started

```bash
git clone https://github.com/mrhobbeys/HyperWorker.git
```

Then tell your AI agent:

> "Read `HARNESS.md` in the HyperWorker folder and build me a harness for [describe your goal]."

That's it. The agent reads HARNESS.md, asks you clarifying questions, scaffolds your project from the templates, runs a verification checkpoint, and begins execution.

**Want to understand the system first?** Read in this order:

1. `HARNESS.md` — the single entry point for the entire system
2. `case-studies/README.md` — pick one that matches your domain
3. Any `core/*.md` file for mechanism details

## Works with

HyperWorker is agent-agnostic. It works with any AI agent that can read files and follow instructions:

- **Claude Code** — subagent-capable, full harness support
- **Cursor** — single-agent mode with rules integration
- **Goose** — MCP-native, recipe-compatible
- **GitHub Copilot** — CLI agent mode
- **Any capable LLM** — if it can read markdown, it can run the harness

## Who this is for

- Operators running long projects through AI agents who are tired of sessions that start strong and fall apart
- Teams using a two-tier setup (planner decomposes and reviews, executor follows instructions)
- Anyone who's felt: "the agent was doing great and then it just... wasn't"

## Why not just use a system prompt?

You can. HyperWorker started that way. Here's what breaks:

**Long projects:** System prompts compress over multiple sessions. The agent forgets constraints from two sessions ago. HyperWorker externalizes state to files the agent re-reads every session.

**Rule conflicts:** When your style guide says "be concise" but your compliance rules say "include the full disclosure," a system prompt gives you no resolution order. The Precedence mechanism resolves conflicts by tier, automatically.

**Scope creep:** The agent "helpfully" edits things it shouldn't touch. HARNESS.md declares boundaries the agent checks before acting.

**Knowledge loss:** What the agent learned on Task 3 is gone by Task 8. The Memory mechanism captures, scopes, and ages knowledge on purpose.

**Unverified claims:** The agent says "done" but didn't actually check. The Verification mechanism requires evidence, not assertions.

HyperWorker is not a replacement for prompting — it's what you add when prompting alone stops scaling.

## Structure

```
HARNESS.md             — self-bootstrapping entry point (read this first)
core/                  — the six mechanisms
templates/             — config, task, project, and executor-prompt skeletons
reference/             — validation, failure modes, optional research protocol
case-studies/          — five worked examples across different domains
starter/               — quick-start for new operators
CHANGELOG.md           — version history
VISION.md              — opinionated scope document
```

## What this is NOT

**Not a hosted product.** No web UI, no dashboard, no cloud service. HyperWorker is markdown and YAML files in a Git repo.

**Not multi-user.** Designed for one operator (one human + AI). Multi-user handoff patterns don't exist yet.

**Not for one-shot tasks.** If you're doing single-prompt work, you don't need a harness. This is infrastructure for real projects that span multiple sessions over days or weeks.

**Not magic.** The agent still has to be capable enough to follow file-system instructions. HyperWorker gives the structure; the model has to read and follow it.

## The recursive proof

The marketing campaign for the original launch was managed by HyperWorker itself. Sixteen tasks across four phases. Every draft, every channel, every review checkpoint — run through the harness. The planner decomposed the work, executors handled individual tasks, and the state file tracked progress across sessions.

v4.0 incorporates lessons from blind testing across five domains and research into Anvil's verification ledger, Karpathy's ratchet pattern, and the emerging harness engineering discipline.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Short version: we want case studies, better templates, and validation tooling. We don't want scope expansion.

## License

MIT — see [LICENSE](LICENSE).

---

*Built by [@mrhobbeys](https://x.com/mrhobbeys).*
