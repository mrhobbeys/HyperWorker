# HyperWorker

A domain-agnostic project management harness for LLM agents. Built so a capable model (orchestrator) can drive a cheaper model (worker) through a long-running project without drift, context loss, or scope creep.

Version: 3.1

## What this is

An LLM left alone on a multi-step project will forget the plan, invent new requirements, edit files it shouldn't touch, and declare "done" on work that isn't finished. HyperWorker prevents that with five enforced mechanisms:

1. **Lock** — one task active at a time. No parallel drift.
2. **Atomicity** — tasks have binary done states. No "mostly finished."
3. **Dependency** — downstream work cannot start until upstream is verified.
4. **Memory Pipeline** — what the agent learns gets scoped, tagged, and carried forward or decayed on purpose.
5. **Precedence** — when rules conflict, tiered resolution decides. No hung agents.

Plus a machine-readable `HARNESS.manifest` that declares which files are infrastructure versus project, so the agent knows its boundaries before it touches anything.

## Who this is for

- Operators running long projects through Claude, GPT, or similar models
- Teams using a two-tier setup (expensive orchestrator, cheap worker)
- Anyone tired of "the agent was doing great and then it just... wasn't"

## Structure

```
HARNESS.manifest       — machine-readable boundary declaration
core/                  — the five mechanisms
templates/             — config, task, project, and worker-prompt skeletons
reference/             — validation, failure modes, optional research protocol
case-studies/          — five worked examples across different domains
starter/               — quick-start for new operators
CHANGELOG.md           — version history
```

## Getting started

Read in this order:

1. `starter/README.md`
2. `HARNESS.manifest`
3. `core/SYSTEM.md`
4. `case-studies/README.md`

Then pick a case study that matches your domain and use it as a template.

## Status

Private beta. v3.1 is currently in blind testing. Breaking changes expected before public launch.

## License

MIT — see [LICENSE](./LICENSE).
