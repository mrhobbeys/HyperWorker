# HyperWorker Vision

## What HyperWorker Is

HyperWorker is a project management harness for LLM agents. It makes a long-running project survive the thing that normally kills it: the agent losing the plot.

The product is five enforced mechanisms — Lock, Atomicity, Dependency, Memory Pipeline, Precedence — and a machine-readable boundary declaration that tells the agent which files are infrastructure and which are the project it's working on. Everything else in this repo is either a template, a reference document, or a worked case study that demonstrates the mechanisms in practice.

## Design Principles

**The harness is structural, not documentary.** Rules enforced by file structure and a manifest beat rules written in prose that an agent is supposed to remember to follow. When we face a choice between "add another paragraph to a doc" and "add a structural check the agent cannot skip," we pick the structural check.

**The orchestrator is dumb about the domain; the config is smart.** The core mechanisms are domain-agnostic. Domain knowledge lives in the project's `config.yaml`, `00-REFERENCE-rules.md`, and task files — not in the harness. If a feature requires the harness to know whether it's running a marketing project or a software project, that feature is probably misdesigned.

**One active task. One source of truth. One lock at a time.** This is not a style preference. It's the only way to make agent behavior legible across sessions and across operators. Parallelism returns over our dead bodies.

**Memory is scoped, tagged, and decays on purpose.** The pipeline exists to prevent cross-context contamination. Learnings from Project A should not silently color decisions in Project B unless they were explicitly tagged Universal. The default is local.

**Case studies teach mechanisms, not domains.** Each case study exists to showcase one or two mechanisms in action. Adding case studies that duplicate existing mechanism coverage is not additive value — it's noise.

## What HyperWorker Will Not Become

The following requests keep coming up. They are out of scope on purpose.

**A learning system that auto-generalizes across projects.** Memory Pipeline already handles cross-project learning via scope tags set by the operator. An automated learning layer that decides for the operator what generalizes is not a feature — it's a source of contamination. Rejected in Council #5 (v3.1). Not reconsidering without a fundamentally different operational model.

**A feedback loop that "tunes" the harness based on past runs.** Same reason. The harness is a stable structural contract. Mutation of the contract based on inference over past runs is the opposite of what this product does.

**An orchestration layer above the orchestrator.** If an operator needs to run many HyperWorker projects in parallel, that's a process problem, not a harness problem. We are not building a meta-harness.

**Built-in integrations with specific LLM providers, IDEs, or CI systems.** The harness is a file-system contract. It runs anywhere a capable model can read files and follow instructions. Locking to vendor-specific APIs makes it brittle and shrinks the addressable market.

**A web UI, dashboard, or hosted service.** HyperWorker is a repo of markdown and YAML. If someone wants to build a UI on top, that's a downstream project, not core.

**Metrics, analytics, telemetry.** The operator reads task state files to know what's happening. If we need a dashboard to tell whether the harness is working, the harness isn't working.

## What We Would Consider

We'd consider contributions that strengthen what's already there: case studies for underrepresented domains, sharper failure-mode documentation, better templates, tooling that validates HARNESS.manifest or TASK-STATE.yaml against schemas, tighter precedence tier examples, and verification checkpoint refinements.

We'd consider a v4 if — and only if — blind testing at scale reveals a failure mode that the five current mechanisms cannot address. Not before.

## The Bar

A good change to HyperWorker either prevents a specific failure we have observed, or sharpens an existing mechanism. A change that adds a mechanism because "it would be nice to have" fails the bar. A change that makes the harness do more fails the bar. A change that makes the harness do the same thing more reliably passes the bar.
