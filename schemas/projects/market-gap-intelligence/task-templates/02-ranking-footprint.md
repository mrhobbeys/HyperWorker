---
id: T-002
kind: task
schema: market-gap-intelligence
phase: B
risk_level: standard
required_tools: [file_read, file_write, browser]
delivery_mode: constrained
depends_on: [T-001]
consumes:
  - "[OR-001#<short-hash>]"
  - "[CMP-NNN#<short-hash>]"   # ONE business/serp competitor per branch
acceptance_criteria:
  - "For each studied competitor (business + worth-studying serp), pages are inventoried from their actual site (sitemap/crawl), not from memory."
  - "Inferred target queries are SERP-verified for the important pages; ranks marked 'verified pos N', 'inferred-not-verified', or 'no'."
  - "Each footprint cluster has volume + cpc (MEASURED via Planner where available; else marked unknown/OBSERVED) and a posture (moat / gap / contested)."
  - "Output names the competitor's moat (defend), their gaps (client opening), and their strategy in one line."
---

# Task T-002: Ranking Footprint (Q2 — what are they ranking for?)

## Objective
Turn a named competitor into a footprint map: clusters they own and defend vs.
clusters they neglect. Branch one competitor per subtask. Study business and
worth-studying serp competitors; do not waste passes profiling pure aggregators.

## Step-by-Step
1. Read the assigned CMP and OR-001 money_terms.
2. Inventory pages: pull /sitemap.xml or crawl nav+footer. Bucket by role
   (money/service, location, blog/info, trust, conversion). Note patterns
   (location-page systems, deep blog, programmatic).
3. Infer each money/location page's target query (title + H1 + URL + repetition).
   SERP-verify the important ones — inferred ≠ ranking.
4. Attach volume + CPC per cluster via keyword-scanner / Keyword Planner
   (MEASURED). Mark unknown where no data.
5. Set posture: moat (owned/defended), gap (demand they neglect or cover badly),
   contested. Write FP artifacts; for page-level head-to-heads on overlap clusters,
   invoke page-seo-grader.
6. Append to evidence log. Answer @@SCAN markers.

## Completion Report
- Acceptance criteria: <X/Y>
- Competitor profiled: [CMP-NNN#hash]
- Outputs: FP-001…NNN
- Their moat: <clusters>
- Their gaps (client openings): <clusters → feed T-003/T-006>
- Their strategy in one line: <…>
