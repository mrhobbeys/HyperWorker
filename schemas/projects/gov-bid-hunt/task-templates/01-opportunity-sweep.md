---
id: T-001
kind: task
schema: gov-bid-hunt
phase: B
risk_level: elevated
required_tools: [file_read, file_write, web_search, web_fetch, browser]
delivery_mode: constrained
depends_on: [T-000]
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "Each registered SRC was swept for currently-open opportunities (deadline after today)."
  - "Each open opportunity is captured as a Finding: title, issuer, state, solicitation #, type, set-aside, close date, link, fit note, eligibility flag."
  - "No fabricated numbers/deadlines; unverified fields marked 'unconfirmed'."
  - "Past-deadline finds recorded as excluded-after-discovery with the date."
---

# Task T-001: Opportunity Sweep

## Objective
Find every currently-open opportunity for this segment across the watch list.

## Steps
1. Read OR-001 and the SRC inventory.
2. Sweep each SRC. For js/login-gated portals, use a browser session; if unavailable, record the portal as a capability gap to revisit, don't skip silently.
3. Consider fanning out subagents (one per source cluster) with web_search + web_fetch.
4. Capture each open opportunity as a Finding with all fields + an eligibility flag (e.g., "blocked: SAM.gov" for federal if not yet active).
5. Record past-deadline items as excluded-after-discovery (with date) so they aren't re-chased.

## Completion Report
- SRCs swept: <X/Y> (gated/uncovered: <list>)
- Findings produced (open): <IDs>
- Excluded-after-discovery: <count>
- Notable: <hottest deadlines, best fits>
