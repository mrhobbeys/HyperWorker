![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Version: 5.2.0](https://img.shields.io/badge/Version-5.2.0-blue.svg)

# HyperWorker

**Project management harness for AI agents.**

Your AI agent starts strong — then forgets the plan, invents new scope, and breaks things it shouldn't touch. HyperWorker stops that.

HyperWorker is a repo of markdown and YAML — not a CLI, not a package, not a hosted service. It's a file-system contract any AI agent reads and follows. The harness keeps long-running projects on track: no drift, no invented scope, no "mostly finished," no unproven claims of completion.

---

## The four things that break

If you've run a real project through an AI agent — not a one-shot task, but something with phases, dependencies, and work that spans multiple sessions — you've probably hit the wall:

1. **It drifts.** The agent invents scope, edits files outside its lane, or decides it knows better than the plan.
2. **It loses context between sessions.** Close the session, open it tomorrow, and decisions you made yesterday are gone or quietly contradicted.
3. **It skips steps.** No verification, no tracking — things get marked "done" that aren't done.
4. **There are no natural checkpoints.** You're reviewing constantly instead of at boundaries, because there are no boundaries.

HyperWorker was built to fix all four.

## How it works

Five mechanisms enforce the four things that were breaking:

**Lock** stops the drift. Only one project can be active at a time. Everything else goes on the backlog. Switching is a deliberate act, not a distraction.

**Atomicity** kills "mostly finished." Every task is a self-contained unit designed for one AI session. Complete or not complete. No "90% done." A task declares the tools it needs; tools it doesn't need aren't available to the agent at all — so "the agent shouldn't have touched that" stops being a request and becomes a fact.

**Typed Artifacts** solves the cross-session problem. Decisions, findings, and anti-patterns get written down once, with stable IDs and a hash of their content. When a later task references one, the harness checks the hash still matches what was decided. No quiet contradictions. No memory that drifts between sessions.

**Verification** proves completion. Tasks require evidence trails — not assertions. The harness checks the evidence is fresh and that the artifacts it cites haven't changed underneath it. The ratchet principle: improvements kept, regressions discard the completion claim.

**Precedence** creates natural checkpoints. When rules conflict, tiered resolution decides. Your absolute rules always beat your style preferences. No guessing.

Underneath all five, every action — every artifact written, every task completed — is appended to a single chained log. The state you see is computed from that log. There is no parallel state file the agent can drift away from. If you want to know exactly what happened and in what order, it's all there, verifiable.

## Getting started

```bash
git clone <this-repo>
cd <this-repo>
```

Then tell your AI agent:

> "Read `HARNESS.md`. Bootstrap a project from the `<schema-name>` schema for `<short description>`."

That's it. The agent reads HARNESS.md, asks you clarifying questions, scaffolds your project from the schema, runs a verification checkpoint, and begins execution.

Five schemas ship as defaults:

| Schema | When to use |
|---|---|
| `marketing-campaign` | Lead-gen funnels, email sequences, landing pages, paid ad creative |
| `software-feature-ship` | Schema → API → frontend → tests → deploy |
| `client-onboarding` | Repeatable onboarding flows; cross-client compounding |
| `event-planning` | Real-world events with hard dates and physical vendors |
| `compliance-audit` | SOC 2, ISO, HIPAA, PCI, internal-quality audit prep |

If none fit, the agent scaffolds from default templates and offers to capture your derived schema after the project completes.

**Want to understand the system first?** Read in this order:

1. `HARNESS.md` — the entry point, file structure, bootstrap protocol
2. `core/SUBSTRATE.md` — how the underlying log and projections work
3. The five `core/*.md` mechanism files
4. The schema closest to your work

## Works with

HyperWorker is agent-agnostic. Any AI that can read markdown, append to a file, and follow a documented protocol can operate the harness:

- **Claude (Opus / Sonnet / Haiku)** — see `templates/models/claude-*.yaml`
- **GitHub Copilot CLI** — see `templates/models/github-copilot.yaml`
- **Other capable LLMs** — start with `templates/models/default.yaml` and tune as you observe behavior

Per-model profiles document what each model does *differently*, not which is "better."

## Who this is for

- Operators running long projects through AI agents who are tired of sessions that start strong and fall apart
- Teams using a two-tier setup (planner decomposes and reviews, executor follows instructions)
- Anyone who's felt: "the agent was doing great and then it just... wasn't"

## Why not just use a system prompt?

You can. HyperWorker started that way. Here's what breaks:

**Long projects:** System prompts compress over multiple sessions. The agent forgets constraints from two sessions ago. HyperWorker externalizes state to files the agent re-reads every session.

**Rule conflicts:** When your style guide says "be concise" but your compliance rules say "include the full disclosure," a system prompt gives you no resolution order. Precedence resolves conflicts by tier, automatically.

**Scope creep:** The agent "helpfully" edits things it shouldn't touch. v5.0 doesn't ask it not to — the tools it shouldn't use aren't in its schema.

**Knowledge loss:** What the agent learned on Task 3 is gone by Task 8. Typed artifacts capture decisions and findings as addressable, hash-cited records that survive sessions.

**Unverified claims:** The agent says "done" but didn't actually check. Verification requires evidence, not assertions, and the harness checks the evidence is fresh.

HyperWorker is not a replacement for prompting — it's what you add when prompting alone stops scaling.

## What this is NOT

**Not a hosted product.** No web UI, no dashboard, no cloud service. HyperWorker is markdown and YAML files in a Git repo.

**Not a refactor of v4.1.1.** The diagnosis is different. The mechanisms are different in kind, not just refinement.

**Not for one-shot tasks.** If you're doing single-prompt work, you don't need a harness. This is infrastructure for real projects that span multiple sessions over days or weeks.

**Not finished.** v5.0 is a working hypothesis (see [VISION.md](VISION.md)). Primitives that don't earn their place get retired in v5.1.

**Not magic.** The agent still has to be capable enough to follow file-system instructions. HyperWorker gives the structure; the model has to read and follow it.

---

## What changed from v4.1.1

The earlier versions added rules, checks, and ceremony to make agent behavior reliable. v5.0 takes a different position: **agent compliance should be structurally enforceable, not verbally requested.** Where v4 asked the agent to remember a rule, v5 changes the substrate so the rule is a fact the agent can't violate.

Concretely:

- **Memory pipeline → Typed Artifacts.** Decisions, findings, and anti-patterns are append-only and hash-cited. Stale citations block writes.
- **Per-step session-state writes → replay from the event log.** No parallel state file to fall out of sync.
- **15-rule executor prompt → under 30 lines.** The substrate enforces what the rules used to ask for.
- **Six mechanisms → five plus a substrate.** Dependency folded into Atomicity; capability gates handle ordering and tool boundaries together.
- **`case-studies/` → `schemas/projects/`.** Five worked examples are now executable bootstraps, not static teaching.
- **Pushback Protocol → council escalation.** Triggered structurally, not as a per-task verbal step.

This is a theory, not a finding. Each primitive in v5.0 has an explicit hypothesis and an explicit falsifier (see `core/*.md` §Hypothesis sections). v5.1 will retire whatever fails its falsifier in real use. Read [VISION.md](VISION.md) for the full posture.

There is no migration path. v4.1.1 remains on its own branch as the prior theory. Operators with running v4.1.1 projects complete them on v4.1.1; new projects start on v5.0.

## Structure

```
HARNESS.md             — self-bootstrapping entry point (read this first)
core/                  — the five mechanisms + substrate
templates/             — config, task, project, model-profile skeletons
schemas/               — five worked project bootstraps
reference/             — validation, failure modes, optional research protocol
tools/                 — agent-side helpers
CHANGELOG.md           — version history
VISION.md              — opinionated scope and theory document
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Short version: we want new schemas, sharper failure-mode documentation, and per-model profiles backed by observed behavior. We do not want scope expansion.

## License

MIT — see [LICENSE](LICENSE).

---

*Built by [@mrhobbeys](https://x.com/mrhobbeys).*
