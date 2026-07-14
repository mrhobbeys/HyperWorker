# HyperWorker Vision (v5.0)

## Posture

HyperWorker is a structural test of a hypothesis: that frontier AI harnesses succeed by changing the **substrate** the agent operates against, not by adding rules the agent is asked to remember to follow. v5.0 is the first version that takes this position seriously enough to remove the rule-stacking that v1–v4 accumulated.

This is a theory, not a finding. Each primitive in v5.0 has an explicit hypothesis and an explicit falsifier (see `core/*.md` §Hypothesis sections). v5.1 will retire whatever fails its falsifier in real use, and add only primitives that produce structural checks rather than rule-following requests.

---

## Frame Shift from v4

v1–v4 designed against the question: *"how do we make the agent follow rules reliably?"* The answer compounded — more rules, more verification components, more confirmation gates, three overlapping state files. v4.1.1 sat at the end of that line.

v5.0 abandons that question. The new question: *"how do we make the agent's compliance structurally enforceable rather than verbally requested?"*

Answers that survive that question are different in shape: hashes, citations, projections, manifests, ledgers, schema validation. Anything verifiable without asking the agent whether it complied is a real primitive. Anything that requires the agent's word for it is sand.

---

## The Diagnosis (Hedged)

Three competing diagnoses survived 2025–2026 frontier research, each strong enough to warrant building against:

- **Decision crystallization failure.** Agents act on implicit decisions that were never written down with addressable IDs. Downstream agents step on those decisions because they cannot be cited.
- **Mutable memory failure.** Incremental memory writes compound non-determinism; replay becomes impossible; consolidated summaries lose the decisions that mattered.
- **Verification construction failure.** Agents fail because they lack fast falsifiable feedback. "The agent didn't have the right context" is what an agent says when no signal rejected its first wrong attempt.

v5.0 hedges across all three. Decisions are first-class addressable primitives; mutable memory is replaced by event-sourced projection; verification is a layered pyramid. None of the three is asserted; all are tested empirically.

---

## Operating Principles

**Substrate over rules.** Mainstream harnesses add rules. A file-based PM harness has the structural advantage of computing against files: hashes, citations, projections, manifests. We use it.

**Heavy upfront, light ongoing.** Setup is substantial. Bootstrap a complex project, expect hours. The earlier versions did not fail because of heavy setup — they failed because of repeated mid-execution operator pull-ins. v5.0 concentrates configuration at scaffold time and minimizes runtime intervention.

**Math with words.** v5.0 attempts to make computable a substrate (stochastic word generation) that was not built to be computed against. The primitives that survive are the ones that don't depend on the agent's compliance: hashes, citations, schemas, event-sourced records, projections.

**Theory, not finding.** Each primitive is a hypothesis. The spec lists the hypotheses explicitly so v5.0 can be evaluated empirically and revised.

**Don't soften the breaks.** v5.0 removes the Memory pipeline, per-step session writes, READ-BACK as a separate ceremony, most of the executor-prompt rules, and forced-verbosity instructions. The replacements are different in *kind*, not just refinement. Operators who want the v4.1.1 behavior should run v4.1.1.

---

## What HyperWorker Will Not Become

The following requests recur. They are out of scope on purpose.

**An auto-tuning harness.** A feedback loop that mutates the harness based on past runs is the opposite of substrate-over-rules. Mutation undermines the structural contract.

**A meta-orchestration layer.** If an operator needs many parallel projects, run many harness instances. We do not build a harness-of-harnesses. *(v5.3 clarification, from field evidence: operators who need many instances also need the coordination between them, and three deployments built that layer ad hoc when we refused to name it. The answer stays inside the position — a program is itself a locked project, run from its own instance, bootstrapped from the `program` schema; see `core/LOCK.md` §Programs. No orchestration primitive enters the substrate. If coordination ever needs code — leases, serialized writes, schedulers — that code is a sibling Hyper project, not harness core.)*

**Built-in vendor integrations as load-bearing features.** The harness is files. Per-model profiles document differences declaratively; they do not call vendor APIs.

**A web UI, dashboard, or hosted service.** v5.0 is markdown and YAML. Downstream tools that surface state are welcome; they are not core.

**Telemetry / metrics built into the substrate.** The operator reads files to see state. If a dashboard is needed to see whether the harness is working, the harness is not working.

**A sixth mechanism.** Five mechanisms plus substrate. If a failure mode emerges that cannot be addressed within the five, the priority is to surface the failure mode (not to add a sixth) and check whether the substrate's primitives compose to handle it. If they genuinely cannot, *then* we consider a sixth — with a falsifiable hypothesis stated up front.

---

## What We Would Consider

- **New schemas** for under-represented domains, with the same depth as the marketing-campaign schema.
- **Sharper failure-mode documentation** in `reference/FAILURE-MODES.md` based on real v5.0 use.
- **Per-model profiles** for additional models, citing observed behaviors with evidence.
- **Council-composition patterns** — different convergence rules for different verification contexts.
- **Compression algorithm refinements** — better deterministic prose-compression that preserves more meaning while passing tokens through.
- **Cross-family verification UX** — observed patterns of how the cross-family setup actually performs in real council reviews.

---

## The Bar

A change to v5.0 either:

- Produces a structural check the substrate can compute, OR
- Removes a primitive that requires the agent's word.

A change that adds rules without structural enforcement fails the bar. A change that adds a primitive whose hypothesis we can't falsify fails the bar.

We measure once: it either holds, or it doesn't. The substrate either catches the failure mode the hypothesis claims, or it doesn't. v5.1 is the version that retires what didn't.
