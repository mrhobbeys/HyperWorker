---
id: T-000
kind: task
schema: opportunity-hunt
phase: A
risk_level: standard
required_tools: [file_read, file_write, web_search, web_fetch]
delivery_mode: constrained
depends_on: []
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "OR-001 records the real eligibility/membership status (co-op vendor awards, partner program enrollments, grant registrations, marketplace accounts) that gates this channel's pursuits."
  - "Every source/program that posts this channel's opportunities is registered as a SRC artifact with access + registration_status + cadence."
  - "Each gating fact (e.g., partner enrollment not active) is reflected so downstream tasks flag blocked opportunities."
---

# Task T-000: Access/Eligibility + Source Inventory

## Objective
Establish the pursuit gate (what we are and aren't eligible for) and the watch list (where this channel's opportunities post).

## Steps
1. Read OR-001. Confirm eligibility/membership status; if stale, web-check the key memberships/enrollments/registrations and supersede OR-001 if needed.
2. List the sources/programs/marketplaces that post THIS channel's opportunities in the in-scope geographies (official/primary sources first, then aggregators).
3. For each, register a SRC artifact: url, source_type, access (open / js-gated / login-gated), registration_status, cadence.
4. Note which sources need a browser session (js/login-gated) so the sweep task can plan for it.
5. Answer @@SCAN-elig and @@SCAN-cadence.

## Completion Report
- Acceptance criteria: <X/Y>
- OR superseded? <yes/no>
- SRCs produced: SRC-001..NNN
- Gated sources needing browser: <list>
- Blocking eligibility facts: <e.g., co-op vendor award not held — affected Findings will be flagged blocked>
