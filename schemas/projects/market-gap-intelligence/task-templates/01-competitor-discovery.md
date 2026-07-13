---
id: T-001
kind: task
schema: market-gap-intelligence
phase: B
risk_level: standard
required_tools: [file_read, file_write, browser]
delivery_mode: constrained
depends_on: [T-000]
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "Every money_term was searched on a LIVE SERP this run (logged-out/incognito-style noted if personalization may skew). web_fetch alone is insufficient — SERPs are client-rendered."
  - "Every competitor artifact has found_on (the query it surfaced on), comp_type, beatable, provenance, captured_date."
  - "comp_type separates business rivals from serp-traps (software/aggregator/publisher/forum) and answer-engine citations. Mixing them fails Tier 3."
  - "The operator's originally-named rivals are each confirmed by a SERP appearance OR explicitly demoted to not-an-SEO-threat with reason."
  - "If a money term's SERP is trap-owned, a finding with intel_role: channel is registered (feeds T-007)."
---

# Task T-001: Competitor Discovery (Q1 — who is the REAL competitor?)

## Objective
Replace assumed rivals with whoever actually owns the SERP, map pack, and AI
overview for the money terms. Branchable: one money-term-cluster per branch.

## Step-by-Step
1. Read OR-001 (money_terms, geography, buyer). For local geo, also search
   `[service] [city]` and `[service] near me`.
2. For each money term, load the live SERP (browser). Capture in order: local/map
   pack (3 + more places), top ~10 organic and the entity behind each, ads
   (commercial signal), AI Overview + its cited sources, SERP features (PAA,
   forums block).
3. Classify every entity into comp_type:
   - **business** — same service/buyer, beatable head-to-head → write CMP, beatable: yes/hard.
   - **serp-trap** — software vendor, directory/marketplace (Clutch, G2, Capterra,
     Yelp, Angi), national publisher, Reddit/Quora, manufacturer. Ranks but is not a
     rival to copy → write CMP with beatable: no, and a channel finding.
   - **answer-engine** — cited by the AI Overview → note beatability of the sources.
4. Test the operator's named rivals: rank for the money terms → real opponent;
   absent → demote to not-an-SEO-threat (may still be a sales threat — note it).
5. Register channel findings (intel_role: channel) for any trap-owned term.
6. Append all artifacts to evidence/EVIDENCE-LOG.md. Answer @@SCAN markers.

## Guidance
A first page owned by software/aggregators is a CHANNEL finding, not a competitor
list — say so loudly; do not seed targets that try to out-content a trap.

## Completion Report
- Acceptance criteria: <X/Y>
- Citations consumed: [OR-001#…]
- Outputs: CMP-001…NNN; channel findings F-NNN
- Real head-to-head rivals: <list>
- Channel traps flagged: <list + which terms>
- Operator assumptions confirmed / overturned: <list>
- Suspected gaps for T-003: <competitor blind spots noticed>
