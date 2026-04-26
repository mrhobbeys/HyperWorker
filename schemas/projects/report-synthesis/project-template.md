# PROJECT.md — {{ project_name }}

## Synthesis purpose

{{ synthesis_purpose }}

## Target audience

{{ target_audience }}

## Output format

{{ output_format }}

## Source corpus

Source reports for this synthesis live in: `{{ input_folder }}`

After bootstrap, the agent registers each file as a `source` artifact in `00-source-inventory`. Sources are immutable once registered; corrections become new source artifacts with `supersedes` pointing at the older one.

## Weighting rule

{{ weighting_rule }}

This rule is applied during claim extraction and contradiction resolution. Operator-set source weights (primary | secondary | contextual) override the default rule on a per-source basis.

## Excluded topics

{{ excluded_topics }}

## Confidence floor

Output claims require at least `{{ confidence_floor }}` confidence. Provisional claims may cite provisional findings; validated claims require operator-promoted findings.

## Deliverable

Final synthesis output: `{{ deliverable_path }}`

## Phase shape

**Phase A — Setup.** Source inventory + synthesis charter. OR-001 declared.

**Phase B — Extraction.** Per source, extract claims as `claim` artifacts. Capture earlier-round wrong-turns as anti-patterns.

**Phase C — Reconciliation.** Find and resolve contradictions across sources.

**Phase D — Synthesis.** Decide structure, draft, audit, finalize.

## Hard scope boundaries

- The synthesis cannot make claims unsupported by registered sources.
- The synthesis cannot include content covering `excluded_topics`.
- Earlier-round source content that was later corrected is not used as live claims; it appears as anti-patterns referenced where the synthesis takes a different direction.
- Operator review is required before final synthesis is written to deliverable_path.

## Completion criteria

- Every registered source has status: incorporated | contradicted-and-resolved | discarded.
- Every claim in the synthesis output cites at least one source by hash.
- All contradictions are resolved or deferred with operator approval.
- Council pass at completeness-audit (critical risk).
- Operator approval at final-synthesis.
