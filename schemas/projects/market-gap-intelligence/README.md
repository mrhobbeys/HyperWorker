# Schema: market-gap-intelligence

## What this is for
One client (or your own business) plus a market question — "how do we rank this",
"niche vs generalist", "which vertical", "what content wins" — produces
evidence-graded competitive and gap intelligence and a target recommendation. It
exists to kill one failure mode: an agent reasoning fluently from priors and news
and shipping a confident strategy never checked against what competitors do or
what buyers search. **Fluency is not evidence.**

## The four intelligence questions (the spine)
Run in order; each task answers one:
1. **Who is the REAL competitor?** Discovered from live SERPs, classified beatable-rival vs channel-trap (software/aggregator/publisher/forum). (T-001)
2. **What are they ranking for?** Footprint map: moat (defend) vs neglected gap (your opening). (T-002)
3. **What are people asking that nobody answers well?** Demand WITH a weak/missing answer. (T-003)
4. **What should we rank for?** Winnable × commercial × fit, with funnel math on measured inputs. (T-006)

## When to use it
- You need to decide where to point SEO/content/ad effort for a client and want it grounded in reality.
- You're choosing niche vs generalist or between verticals (set scope_mode: vertical-choice; T-004 fires).
- You manage many clients and need one repeatable, isolated project per client.

## When NOT to use it
- One-shot keyword curiosity (use the keyword-scanner skill directly).
- Pure local map-pack execution for a single page (use local-search-ranking-planner).
- No live data tools available at all — the schema's whole value is MEASURED checking; without any tool reach, most findings degrade to OBSERVED/ASSUMED and the run can only produce hypotheses.

## What the schema gives you
**Provenance enforcement.** Every evidence-bearing artifact carries MEASURED /
OBSERVED / ESTIMATED / ASSUMED. Layer 2 (`recommendation_evidence_floor`) rejects
any shipped recommendation resting on ASSUMED inputs alone.

**Discovery honesty.** `competitor_source_check` rejects any competitor with no
`found_on` query — memory-sourced rivals cannot leak in.

**Channel-trap surfacing.** `channel_trap_surfacing` forces a channel-call when a
money term's SERP is owned by software/aggregators/forums, so you never recommend
out-content-ing an opponent you can't beat.

**Hypothesis challenge.** `disconfirming_finding_present` fails a critical run with
zero disconfirming findings — if everything confirmed the operator's prior, the run
under-searched.

**Client isolation.** One project per client; `client_scope_isolation` blocks
cross-client bleed. Method lives in the schema, facts live in the project — broad
storage, laser focus.

## Phase shape
- **A — Frame.** Client dossier + OR (T-000).
- **B — Discover.** Competitor discovery (T-001) → footprint (T-002) → gap mining (T-003). Council after the phase audits discovery honesty + traps.
- **C — Evaluate.** Vertical evaluation (T-004, conditional) + anti-pattern capture (T-005) + target selection with funnel math (T-006).
- **D — Recommend.** Channel-reality audit (T-007) → recommendation synthesis (T-008) → evidence-integrity audit + council (T-009).

## New artifact kinds
`competitor` (CMP) · `footprint` (FP) · `gap` (GAP) · `target` (TGT). Plus a
`provenance` extension on `finding`, an `intel_role` extension on `decision`, and a
`prior_direction` extension on `anti-pattern`.

## Companion skills (work with or without the harness)
This schema pairs with the standalone Market-Intelligence-System skills:
competitor-finder, serp-rank-profiler, question-gap-miner, vertical-evaluator,
client-dossier — plus the operator's existing keyword-scanner,
local-search-ranking-planner, and page-seo-grader. Inside the harness, a task
*invokes* the skill; outside it, the skill runs solo at lower ceremony.

## Bootstrap
```
hw bootstrap --schema market-gap-intelligence --name <client-id>
```
Asks for the decision, client URL, geography, buyer, money terms, scope mode,
brand constraints, available tools, confidence floor, deliverable path. The
project.activate council confirms the OR is real (geo not inherited, brand limits
declared) before discovery begins.
