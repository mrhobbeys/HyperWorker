# Schema: report-synthesis

## What this is for

You have a pile of related reports — audits, research deep-dives, competitive briefs, interview notes, prior analyses, multiple correction rounds — and you need to integrate them into a single source-of-truth document that downstream work can consume reliably.

The synthesis is not a summary. Summaries lose decisions. This schema produces a structured deliverable where every claim cites a source by content hash, every input source is accounted for, contradictions between sources are surfaced and resolved as Decisions, and earlier-round wrong-turns are captured as Anti-Patterns rather than silently dropped.

## When to use it

- Multiple reports cover the same domain with different angles, depths, or correction rounds.
- The operator has explicit constraints, goals, or weighting rules to apply to the corpus.
- The deliverable will be consumed by humans or by future tasks that need to trace claims to sources.
- Disagreement between sources is real (not just rephrasing) and resolution matters.
- You're building strategic foundation that downstream work depends on.

## When NOT to use it

- The reports are highly redundant and you just want a TLDR. Use a one-shot summary instead.
- There is no operator goal to align the synthesis against (synthesis without purpose is just collation).
- Sources don't disagree meaningfully — there's nothing to reconcile.
- The deliverable is throwaway and citation integrity isn't worth the cost.

## What the schema gives you

**Source-fidelity enforcement.** Layer 1 verification rejects any synthesis claim that doesn't cite a `source` artifact by hash. The agent cannot smuggle "well, generally speaking..." prose into the output.

**Coverage auditing.** Every input source has to be processed: incorporated, contradicted, or explicitly discarded with reason. Coverage is structurally auditable.

**Round-aware processing.** Sources tagged with `round: initial | notes | draft | final` get weighted per the declared `weighting_rule`. Earlier-round content that was later corrected becomes anti-patterns ("X was the initial direction; corrected to Y because Z") — preserved as cautionary signal rather than ignored.

**Contradiction surfacing.** When sources disagree, the harness forces a `contradiction` artifact to be created and resolved via a Decision with explicit `alternatives_considered`. The agent cannot paper over disagreements.

**Operator-goal alignment.** The synthesis is built against a declared operator goal (OR-001). Council role `operator-goal-aligner` rejects work that drifts from the stated purpose.

**Trace integrity.** The final synthesis projection includes hash citations to every source claim. If a source is later corrected or removed, the citation goes stale and is structurally detectable.

## Phase shape

**Phase A — Setup.** Source inventory + synthesis charter. Operator declares OR-001 (purpose, audience, scope, weighting rule, deliverable shape).

**Phase B — Extraction.** Per source: extract claims as typed artifacts. Capture wrong-turns from earlier rounds as anti-patterns.

**Phase C — Reconciliation.** Find contradictions across sources. Resolve each via Decision artifact with explicit alternatives.

**Phase D — Synthesis.** Decide output structure. Fill the structure with cited claims. Council audits for completeness and citation integrity. Operator reviews and approves.

## What this schema is NOT

A literature review generator. The schema does not require comprehensive treatment of every related work — it requires comprehensive treatment of *every source the operator dropped in*. Selectivity is the operator's job; coverage of what's selected is the harness's job.

A multi-author writing tool. One operator + one or more agents. Multi-operator handoff is not modeled.

A plagiarism detector. Source citation is for traceability of synthesis claims, not for detecting copied content.

## Bootstrap

```
hw bootstrap --schema report-synthesis --name <project-id>
```

The schema asks for purpose, audience, output format, input folder, weighting rule, excluded topics, confidence floor, and deliverable path. After bootstrap, drop your sources into the declared input folder and run the first task.
