# Schema: content-piece-test

Working schema for one piece of creator content. Inherited from `report-synthesis` and rewritten for the creator-content-pipeline use case. Saved as the generic `content-piece` schema after `hw wrap` if the empirical run validates the patterns.

## What this is for

You have raw inputs (tweets, voice memos, originating articles, notes) and you want one piece of content distributed across several publication-format-native variants — each written to its channel's actual shape, not a paraphrase of the others. The schema ships with a three-format default example (Substack longform, X longform, YouTube lead-ins) worked through every task template; the operator declares their actual target formats (`target_formats` at bootstrap, captured verbatim in OR-001.formats) — a newsletter + LinkedIn + a podcast script, or any other combination, works the same way.

The schema captures the operator's voice as a load-bearing OR field, supports an optional default lens for finding angles when none is supplied, runs an interactive interview with a hard question budget, captures verbatim "lines that sound like the operator" as their own artifact kind, and generates the declared variants in a single ab-variant task with hash-citation freshness on the verbatim keepers.

## When to use it

- One piece of creator content distributed across multiple formats.
- The operator's voice is distinctive and load-bearing (not a corporate tone).
- The interview / rough-draft loop matters; it's not just summarizing existing material.

## When NOT to use it

- Synthesizing a corpus of reports into a single document. Use `report-synthesis`.
- Marketing campaign with offer mechanics. Use `marketing-campaign`.
- One-shot summary of a single source. Out of scope.

## Phase shape

**Phase A — Setup.** Source inventory + corpus scan. OR-001 declared, central angle confirmed or surfaced.
**Phase B — Interview.** Interactive turn-by-turn interview. Findings emit per operator response.
**Phase C — Draft capture.** Operator pastes rough draft; agent flags verbatim_keepers; operator approves keeper list.
**Phase D — Format generation.** ab-variant single-task three-variant pass.
**Phase E — Council & wrap.** Five council members fire on T-004; on PASS, hw wrap + hw schema save.

## Bootstrap

```
hw bootstrap --schema content-piece --name <piece-slug>
```

(For the first piece, this schema is `content-piece-test`; on `hw wrap` it gets saved as the generic `content-piece` for piece 2 onward.)

## What's novel vs report-synthesis

- `voice_anchor: list[string]` as load-bearing OR field (inheriting the v5.1 brand_voice_anchor widening pattern, applied outside marketing-campaign)
- `verbatim_keeper` artifact kind (new, prefix VK)
- Operator-declared publication formats as `ab_variant_axis` (default example: three — Substack longform, X longform, YouTube lead-ins; count and shape come from `target_formats` at bootstrap)
- `interview_question_budget` Layer 1 check declared in capability-gates.yaml
- `refuse-rather-than-pad` thinness protocol
- T-002 (interview) runs in parent context, not subagent — turn-by-turn visibility for question-budget Layer 1
