# Ranking Test via HAIKU subagents — explicit instructions

> Used in phase T-006. Purpose: measure how the site ranks for its target queries AND detect
> DUPLICATE / STOLEN content (copies outranking the originals). Output feeds the DMCA phase (T-007).

## Why Haiku
Run these as HAIKU subagents (Agent tool, `model: haiku`): the task is narrow, mechanical, and
parallel (one query/snippet per subagent). Give each subagent EXPLICIT, fixed instructions and a
strict output schema — do not ask Haiku for open-ended reasoning.

## What to test
1. **Target queries:** pull the site's queries-with-impressions from GSC (and obvious money/topic
   keywords). One subagent per query (or small batch).
2. **Scraper-detection snippets:** take ~12–18 word VERBATIM snippets from the site's most
   distinctive / highest-value articles. One subagent per snippet.

## Per-subagent instruction template (give this verbatim to each Haiku subagent)
```
You are a ranking-and-duplicate-content checker. Do a web search for the EXACT input below and
report only what the results show. Do not speculate.

INPUT: "<query OR verbatim snippet>"
OUR SITE: <site_domain>

Return STRICT JSON only:
{
  "input": "<the input>",
  "our_url": "<our ranking URL or null>",
  "our_position": <integer rank in top 20, or "not_in_top_20">,
  "competing_results": [{"rank": <n>, "url": "<url>", "title": "<title>"}],
  "duplicate_flags": [
    {"url": "<non-our-site URL>", "match_type": "verbatim|near",
     "evidence_snippet": "<<=15 words copied from our content>"}
  ]
}
Rules: duplicate_flags = any NON-<site_domain> URL whose text matches our passage (sign of scraping).
Quote <=15 words as evidence. If none, return []. JSON only, no prose.
```

## Orchestration
- Dispatch N subagents in parallel; collect their JSON.
- Aggregate to `outputs/ranking-test-results.md`: a table of input -> our_position -> top competitors,
  and a separate **Duplicate/Scraper list** (input, copying URL, evidence snippet).
- Hand the Duplicate/Scraper list to the DMCA phase (T-007).

## Caveats
Search results vary by location/personalization and are directional, not absolute. Re-run flagged
items for stability before treating a duplicate as confirmed.
