# Contributing to HyperWorker v5.0

v5.0 is a structural test of a hypothesis. The bar for changes is high. This document explains what we want, what we don't, and how contributions are evaluated.

## What we want

- **New project schemas.** Domains under-represented in the five defaults. Each schema must include the full set: `schema.yaml`, `precedence-tiers.yaml`, `artifact-extensions.yaml`, `capability-gates.yaml`, `verification.yaml`, `council.yaml`, `project-template.md`, `rules-template.md`, `task-templates/`, README. Bar: meaningfully different from existing schemas (different domain extensions, different council composition, different default tasks). Use the marketing-campaign schema as the structural reference.

- **Per-model profile additions.** A new profile for a model not yet in `templates/models/`. Cite observed behaviors with evidence — postmortems, framework docs, sample-size-disclosed observations. Do not declare a model "worse" than another.

- **Sharper failure-mode documentation.** `reference/FAILURE-MODES.md` should grow as v5.0 is observed in real use. Document failures that fall *outside* any hypothesis in the spec — these indicate missing primitives.

- **Structural check refinements.** Better citation-validation logic, tighter recitation overlap heuristics, deterministic compression improvements. Each refinement must produce an effect verifiable without asking the agent if it complied.

- **Council convergence-rule additions.** New convergence patterns for new verification contexts. Document the trigger that motivates each pattern.

## What we don't want

- **A sixth mechanism.** Five mechanisms plus substrate. If a failure mode you observe seems to require a sixth, the first ask is: does the substrate's primitives compose to handle it? If genuinely not, surface the failure mode in an issue with the falsifiable hypothesis a sixth mechanism would test. Do not submit a sixth-mechanism PR cold.

- **Verbal-rule additions to the executor prompt.** The 30-line bound is load-bearing. If the agent needs to know something, encode it in the substrate (a schema, a citation, a Layer 1 check) — not as a rule the agent is asked to follow.

- **Auto-tuning, feedback loops, meta-orchestration, dashboards, hosted-service features.** All explicit non-goals (see `VISION.md` §What HyperWorker Will Not Become).

- **CLI implementations of `hw`.** `hw` is an agent protocol, deliberately. A binary CLI is a downstream tool, not core. We won't merge a Python or Node implementation that becomes the new dependency for using the harness.

- **Migration tooling from v4.1.1.** v5.0 is a clean break. Helping operators move artifacts from one harness to another is welcome as a separate downstream project; it is not part of v5.0.

## The bar

A change must either:

1. **Produce a structural check** the substrate can compute without asking the agent if it complied, OR
2. **Remove a primitive** that requires the agent's word.

A change that adds rules without structural enforcement fails the bar. A change that adds a primitive whose hypothesis we can't falsify fails the bar.

## How to contribute

1. Open an issue describing the failure mode the change addresses, or the schema/profile gap.
2. Reference which mechanism(s) are involved.
3. If submitting a PR, include a before/after showing the structural check (what the substrate now verifies that it didn't before).
4. For schema PRs, include a sample bootstrap walkthrough demonstrating the schema in use.

## Code of conduct

Be constructive. Be specific. Respect the scope boundaries.
