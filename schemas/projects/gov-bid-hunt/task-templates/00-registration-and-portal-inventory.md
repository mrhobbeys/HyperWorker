---
id: T-000
kind: task
schema: gov-bid-hunt
phase: A
risk_level: standard
required_tools: [file_read, file_write, web_search, web_fetch]
delivery_mode: constrained
depends_on: []
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "OR-001 records the real registration/eligibility status (SAM.gov, state portals, set-aside certs) that gates this segment's bidding."
  - "Every portal/source that posts this segment's work is registered as a SRC artifact with access + registration_status + cadence."
  - "Each federal-gating fact (e.g., SAM.gov not active) is reflected so downstream tasks flag blocked opportunities."
---

# Task T-000: Registration + Portal Inventory

## Objective
Establish the bidding gate (what we are and aren't eligible for) and the watch list (where this segment's work posts).

## Steps
1. Read OR-001. Confirm registration/eligibility status; if stale, web-check SAM.gov entity status and key state/tribal portals and supersede OR-001 if needed.
2. List the portals/aggregators/agencies that post THIS segment's opportunities in the in-scope geographies (official portals first, then aggregators like BidNet/DemandStar).
3. For each, register a SRC artifact: url, source_type, access (open / js-gated / login-gated), registration_status, cadence.
4. Note which portals need a browser session (js/login-gated) so the sweep task can plan for it.
5. Answer @@SCAN-elig and @@SCAN-cadence.

## Completion Report
- Acceptance criteria: <X/Y>
- OR superseded? <yes/no>
- SRCs produced: SRC-001..NNN
- Gated portals needing browser: <list>
- Blocking eligibility facts: <e.g., SAM.gov not active — federal Findings will be flagged blocked>
