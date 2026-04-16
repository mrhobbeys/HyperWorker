![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Version: 3.1.1](https://img.shields.io/badge/Version-3.1.1-blue.svg)
![Built for: Claude Cowork](https://img.shields.io/badge/Built%20for-Claude%20Cowork-blueviolet.svg)

# HyperWorker

**Make your Cowork HyperWork.**

Your AI agent starts strong — then forgets the plan, invents new scope, and breaks things it shouldn't touch. HyperWorker stops that.

HyperWorker is a project management harness for LLM agents. Five enforced mechanisms keep long-running projects on track: no drift, no invented scope, no "mostly finished."

<!-- TODO: Replace with demo GIF or structural diagram
     Options:
     1. Annotated screenshot of the file tree showing harness vs. project boundary
     2. GIF of a Cowork session: operator says "next step" → agent reads task → produces draft → stops
     3. Mermaid diagram of the five mechanisms
     4. YouTube thumbnail linking to walkthrough video
-->

---

## The four things that break

If you've run a real project through Claude Cowork — not a one-shot task, but something with phases, dependencies, and work that spans multiple sessions — you've probably hit the wall:

1. **It drifts.** The agent invents scope, edits files outside its lane, or decides it knows better than the plan.
2. **It loses context between sessions.** Close Cowork, open it tomorrow, and the agent has no idea what happened yesterday.
3. **It skips steps.** No verification, no tracking — things get marked "done" that aren't done.
4. **There are no natural checkpoints.** You're reviewing constantly instead of at boundaries, because there are no boundaries.

HyperWorker was built to fix all four.

## How it works

HyperWorker is a repo of markdown and YAML — not a CLI, not a package, not a hosted service. It's a file-system contract that Claude reads and follows inside Cowork.

Five mechanisms enforce the four things that were breaking:

**Lock** stops the drift. Only one task can be active at a time. The agent picks up a task, works on it, and completes it before touching anything else. No parallel drift, no scope invention.

**Atomicity** kills "mostly finished." Tasks have binary done states. Complete or not complete. No "90% done" and no "I'll come back to that."

**Dependency** prevents skipped steps. Downstream tasks can't start until upstream tasks are verified. If Task 3 depends on Task 2, and Task 2 hasn't been checked off, Task 3 stays blocked.

**Memory Pipeline** solves the cross-session problem. What the agent learns gets scoped, tagged, and carried across sessions in the file system. Start a new Cowork session tomorrow, point Claude at `HARNESS.manifest`, and it knows exactly where you left off — every task, every dependency, every checkpoint.

**Precedence** creates natural checkpoints. When rules conflict, tiered resolution decides. Your absolute rules always beat your style preferences. Phase gates emerge naturally from the dependency structure. You review at boundaries, not constantly.

Plus a machine-readable `HARNESS.manifest` that declares which files are infrastructure versus project, so the agent knows its boundaries before it touches anything.

## Getting started

```bash
git clone https://github.com/mrhobbeys/HyperWorker.git
```

Then tell your AI agent:

> "Read `HARNESS.manifest` in the HyperWorker folder and build a harness for [describe your project]."

That's it. The agent reads the manifest, asks you clarifying questions, and scaffolds your project from the templates.

**Want to understand the system first?** Read in this order:

1. `HARNESS.manifest` — what's infrastructure vs. what's your project
2. `core/SYSTEM.md` — the five mechanisms
3. `case-studies/README.md` — pick one that matches your domain

## Who this is for

- Operators running long projects through **Claude Cowork** who are tired of sessions that start strong and fall apart
- Teams using a two-tier setup (orchestrator plans and reviews, worker executes)
- Anyone who's felt: "the agent was doing great and then it just… wasn't"

## Why not just use a system prompt?

You can. HyperWorker started that way. Here's what breaks:

**Long projects:** System prompts compress over multiple sessions. The agent forgets constraints from two sessions ago. HyperWorker externalizes state to files the agent re-reads every session.

**Rule conflicts:** When your style guide says "be concise" but your compliance rules say "include the full disclosure," a system prompt gives you no resolution order. The Precedence mechanism resolves conflicts by tier, automatically.

**Scope creep:** The agent "helpfully" edits things it shouldn't touch. `HARNESS.manifest` declares boundaries in a machine-readable format the agent checks before acting.

**Knowledge loss:** What the agent learned on Task 3 is gone by Task 8. The Memory Pipeline captures, scopes, and ages knowledge on purpose.

HyperWorker is not a replacement for prompting — it's what you add when prompting alone stops scaling.

## Structure

```
HARNESS.manifest       — machine-readable boundary declaration
core/                  — the five mechanisms
templates/             — config, task, project, and worker-prompt skeletons
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

The marketing campaign for this launch was managed by HyperWorker itself. Sixteen tasks across four phases. Every draft, every channel, every review checkpoint — run through the harness in Cowork. The orchestrator planned the work, workers executed individual tasks, and the state file tracked progress across sessions.

v3.1 is the version that survived blind testing across five domains.

## What's next

v3.1 is the current version. Contributions that strengthen what's already here are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).

A v4 would only happen if blind testing reveals a failure mode that the five current mechanisms cannot address. Not before.

For the full design philosophy and explicit non-goals, see [VISION.md](VISION.md).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Short version: we want case studies, better templates, and validation tooling. We don't want new mechanisms or scope expansion.

## License

MIT — see [LICENSE](LICENSE).

---

*Built by [@mrhobbeys](https://x.com/mrhobbeys). Built for Claude Cowork.*
