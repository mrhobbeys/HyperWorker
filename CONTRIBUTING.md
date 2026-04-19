# Contributing to HyperWorker

Thanks for your interest. HyperWorker has a specific scope and a high bar for changes. This document explains what we're looking for and how contributions are evaluated.

## What we want

- **Case studies** for underrepresented domains. The five mechanisms should be stress-tested across as many project types as possible.
- **Sharper failure-mode documentation.** If you find a way an agent breaks through the harness, document it. That's more valuable than a feature request.
- **Better templates.** Config skeletons, task templates, worker-prompt templates — anything that reduces onboarding friction.
- **Validation tooling.** Scripts or checks that validate `HARNESS.md` structure or `TASK-STATE.yaml` against their schemas.
- **Tighter precedence tier examples.** Real-world examples of rule conflicts and how the tier system resolved them.
- **Verification checkpoint refinements.** Better patterns for catching work that's "done" but wrong.

## What we don't want

- **New mechanisms.** The five mechanisms are the product. If something can't be solved within Lock, Atomicity, Dependency, Memory Pipeline, and Precedence, it's out of scope.
- **Scope expansion.** Multi-user handoff, web UIs, dashboards, hosted services, vendor-specific integrations — these are all explicit non-goals. See [VISION.md](VISION.md).
- **Auto-generalization features.** The Memory Pipeline is deliberately scoped. Cross-project learning was rejected after testing.

## The bar

A change must prevent a specific, observed failure or sharpen an existing mechanism. "It would be nice if..." is not enough. Show the failure mode, then show how your change prevents it.

## How to contribute

1. Open an issue describing the failure mode or improvement.
2. Reference which mechanism(s) are involved.
3. If submitting a PR, include a before/after showing the change in action.

## Code of conduct

Be constructive. Be specific. Respect the scope boundaries.
