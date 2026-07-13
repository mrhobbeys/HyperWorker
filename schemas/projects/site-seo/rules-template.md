# 00-REFERENCE-rules.md — <site_domain> SEO Recovery

## Precedence Order
Higher tiers override lower. Tier 1 cannot be overridden.

### Tier 1: SEO-SAFETY-AND-DISCIPLINE (absolute)
- Report-first: propose; operator / dev / server-side crew execute. The worker makes NO live changes.
- COMMIT to one recommended path — never refuse to recommend; separate "my recommendation" from "who executes".
- Operator decisions are FINAL: record verbatim, never re-open or contradict. Raise a concern once, then comply.
- End each phase that surfaces server/dev work with a HANDOFF (outputs/SERVER-HANDOFF-<task>.md).
- Never recommend deindex / redirect / bulk-delete / canonical change without operator approval + rollback.
- Ranking + duplicate-content checks use HAIKU subagents per ranking-test-haiku.md.

@@SCAN_1_1: Confirm this output is a proposal/handoff, not a live change the worker made.
@@SCAN_1_2: If this phase needs server-side work, confirm a SERVER-HANDOFF was produced.

### Tier 2: SCOPE
- Assigned site, SEO only. Sitemap/robots server fixes -> Recovery. DMCA is a late phase.

@@SCAN_2_1: Confirm this is SEO for the assigned site, server work handed off.

### Tier 3: TECHNICAL
- Preserve URLs; recover or 301, don't delete; resubmit only the correct sitemap; valid schema.org.

### Tier 4: DOCUMENTATION
- Keep STATUS.md current; label each server-side handoff clearly.

## Banned Tokens
| Banned | Safe Replacement | Tier | Why |
|---|---|---|---|
| I deindexed | recommend operator deindex | 1 | The SEO worker proposes; never makes live ranking changes. |
