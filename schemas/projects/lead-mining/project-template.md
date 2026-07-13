# PROJECT.md — {{ project_name }} (lead-mining)

## Goal
Mine the operator's own inbound email across {{ accounts }} ({{ date_range }}) for every contact that could be a lead, build ONE verified master list, and capture what each needed.

## Accounts
{{ accounts }}

## Inbound-only rule
Count ONLY people/businesses who EMAILED the operator. Skip anyone the operator only cold-emailed who never replied.

## Exclude
{{ exclude_rules }}

## Current customers
{{ include_current_customers }} (if included, flag as "current — upsell").

## Verification
{{ verify_scope }}

## Deliverable
{{ deliverable_path }}

## Phase shape
A — Setup: confirm exact addresses + connector access; lock filters/date range (OR-001); register each mailbox as a SRC.
B — Harvest & reduce: pull inbound senders per account (fan-out subagents per account/time-window) -> raw contacts (Findings); apply exclude rules; dedupe/merge by person + company/domain.
C — Verify & deliver: enrich (company/role/what-they-do), infer need, status-check (active/cold/customer); compile the master list, prioritize, hand off.

## Scope
- account-inventory-and-access
- inbound-harvest
- filter-and-dedupe
- enrich-and-infer-need
- verify-and-status
- master-list-and-handoff

## Hard boundaries
- Inbound contacts only; never invent contacts or emails. Unverifiable fields = "unconfirmed".
- Exclude vendors, newsletters/automated, internal/personal per rules.
- Operator approval before any outreach is sent (this project produces a LIST, not sends).
- Privacy: this is the operator's own data; do not export contacts to third parties.

## Completion criteria
- Every mailbox harvested for the date range; exclude rules applied; duplicates merged.
- Each lead has: name, email, company, role (best effort), inferred need, status, source mailbox, last-contact date.
- Master list compiled + prioritized; session handoff written.
