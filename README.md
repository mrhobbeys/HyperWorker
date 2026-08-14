![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Version: 6.0.0](https://img.shields.io/badge/Version-6.0.0-blue.svg)

# HyperWorker

**Project management harness for AI agents.**

Your AI agent starts strong — then forgets the plan, invents new scope, and breaks things it shouldn't touch. HyperWorker stops that.

HyperWorker is a repo of markdown and YAML — not a CLI, not a package, not a hosted service. It's a file-system contract any AI agent reads and follows. The harness keeps long-running projects on track: no drift, no invented scope, no "mostly finished," no unproven claims of completion.

## Why this exists

HyperWorker was built by an operator with ADHD, for people whose brains don't keep state between interruptions — and it turns out that's also a precise description of an LLM. Drift, context loss between sessions, novelty-driven scope creep, no object permanence for decisions made twenty minutes ago: these are ADHD-shaped failure modes, and agents have all of them. So the harness is symmetrical on purpose. The same substrate that keeps the agent honest — externalized memory, one active project, structural enforcement instead of "please remember" — is an executive-function prosthesis for the human operating it. Lock is enforced single-tasking with a guilt-free capture slot for the shiny new idea (`hw log` — the idea survives without hijacking the current project). Typed artifacts are working memory that doesn't evaporate. Session handoff is re-entry after interruption. Nothing in this system relies on anyone — human or model — remembering anything.

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

Twenty schemas ship as defaults:

| Schema | When to use |
|---|---|
| `marketing-campaign` | Lead-gen funnels, email sequences, landing pages, paid ad creative |
| `software-feature-ship` | Schema → API → frontend → tests → deploy |
| `client-onboarding` | Repeatable onboarding flows; cross-client compounding |
| `event-planning` | Real-world events with hard dates and physical vendors |
| `compliance-audit` | SOC 2, ISO, HIPAA, PCI, internal-quality audit prep |
| `report-synthesis` | Multi-source research distilled into a cited, contradiction-checked report |
| `site-review-repair` | Broken-site triage after a migration or incident: crawl, diagnose, fix, verify |
| `site-seo` | SEO recovery for an existing site, run as ordered deep-focus phases |
| `site-monetization` | Audit and restore ad revenue: AdSense, Ezoic optimization, video programs |
| `gov-bid-hunt` | Government bid discovery and pursuit for one service-line segment |
| `opportunity-hunt` | Non-government revenue channels: commercial, co-op contracts, partners, grants |
| `lead-mining` | Mine your own inboxes and accounts for inbound leads you already have |
| `single-opportunity` | One specific deal end to end: qualify → propose → submit → close |
| `cleanroom-rebuild` | Rebuild a legacy app from measured behavior — never its code — behind an enforced wall |
| `brand-ecosystem-audit` | Audit a brand across every surface it occupies; synthesize strategic paths, not one fixed plan |
| `market-gap-intelligence` | Four ordered competitive-gap questions answered with MEASURED/OBSERVED evidence, not priors |
| `content-piece-test` | One piece of creator content fanned out to three format-native variants, voice preserved verbatim |
| `book-edit-test` | Voice-preserving re-release edit of a shipped manuscript, per-chapter hermetic passes |
| `course-master-plan-test` | Multi-module course build on a community platform; L1/L2/L3 spawn pattern (working schema) |
| `program` | Orchestrate N concurrent workstreams (each its own harness instance): registry, spawn/promote/retire, roll-up cycles |

If none fit, the agent scaffolds from default templates and offers to capture your derived schema after the project completes.

Two of the twenty deserve a special note. An **ongoing** project (`lifecycle: ongoing`, v5.3) works in cycles with a computed next-due date instead of a terminal "done" — for weekly sweeps, standing registries, maintenance plans. A **program** (v5.3) is how multiple projects run at once without breaking the one-active-project lock: every workstream gets its own harness instance, and the orchestrator coordinating them is itself just a locked HyperWorker project. See `core/LOCK.md` §Ongoing Projects and §Programs.

## Work the way you work

The most expensive thing an agent does to an operator is interrupt them — "yet another question" at every step burns more attention than the work saves, and for some operators each context-switch costs fifteen minutes of momentum. HyperWorker's position: **the harness asks you how you want to be asked, once, at bootstrap — then it stops asking.**

These are existing substrate fields (declared in `OR-001`, see `core/ATOMICITY.md`), not aspirations:

| You want | Declare |
|---|---|
| To approve every substantive move | `delegation_policy.mode: step-by-step` |
| Check-ins at phase boundaries only | `delegation_policy.mode: hybrid` |
| To be left alone until it's done or stuck | `delegation_policy.mode: run-to-completion` + `execution_mode: agent` |
| Specific events to always pause, regardless | `pause_on: [<your triggers>]` |

`execution_mode: agent` runs autonomously up to five non-negotiable safety floors (critical-risk completions, detected smoke-run language, exhausted retries, identity drift, your own mid-flow directives) — autonomy never means unsupervised mutation of things you can't undo. The point is that your interruption budget is a declared constraint the substrate enforces, not a personality trait the agent guesses at.

There is no single right setting. An operator who thrives on tight loops and an operator who needs three uninterrupted hours are both first-class users; they fill in the same field differently.

**Want to understand the system first?** Read in this order:

1. `HARNESS.md` — the entry point, file structure, bootstrap protocol
2. `core/SUBSTRATE.md` — how the underlying log and projections work
3. The five `core/*.md` mechanism files
4. The schema closest to your work

## Works with

**Cowork-first, agnostic always.** HyperWorker's primary tested environment is [Cowork](https://claude.com) (Anthropic's desktop agent) — point a Cowork session at the repo and say the bootstrap line above. But the harness is a file-system contract, not an integration: any AI that can read markdown, append to a file, and follow a documented protocol can operate it. Nothing in the substrate calls a vendor API.

- **Cowork / Claude (Opus / Sonnet / Haiku)** — see `templates/models/claude-*.yaml`
- **GitHub Copilot CLI** — see `templates/models/github-copilot.yaml`
- **Local models** (Ollama, LM Studio, llama.cpp, vLLM) — start with `templates/models/default.yaml` and tune as you observe behavior. Whether a given local model can carry the protocol — and at what token overhead — is an empirical question; [HyperFinch](HyperFinch/) exists to answer it with measurements instead of vibes.

Per-model profiles document what each model does *differently*, not which is "better."

## The Hyper ecosystem

The harness core stays markdown and YAML, permanently. Capabilities that need code or hardware ship as sibling `Hyper<animal>` projects — self-contained repos that compose with the harness without bloating it:

- **HyperFinch** (shipped) — variation → measurement → selection. Sweeps a task across prompt/condition/input variants on a local LLM and reports what actually performs, with honest variance.
- **Voice add-on** (planned, separate repo) — voice-first capture for the moments typing loses the thought: `hw log` a backlog idea, dictate a mid-flow directive, file a friction entry at the speed of speech. An add-on, never a core dependency.

## Who this is for

- Operators running long projects through AI agents who are tired of sessions that start strong and fall apart
- Operators with ADHD — or anyone whose working memory shouldn't be a project's single point of failure
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

**Not finished.** v5.x is a working hypothesis (see [VISION.md](VISION.md)). Primitives that don't earn their place get retired in the next minor version.

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
