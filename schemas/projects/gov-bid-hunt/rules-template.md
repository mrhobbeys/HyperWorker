# 00-REFERENCE-rules — {{ project_name }} (gov-bid-hunt)

Precedence tiers resolve rule conflicts (see precedence-tiers.yaml). Highest tier wins.

## Tier 1 — ABSOLUTE (never overridden)

- Never recommend submitting a bid the business is not currently eligible to submit. Flag the eligibility gate (e.g. "blocked: SAM.gov") instead of dropping the opportunity.
- Never fabricate a solicitation number, deadline, set-aside, or agency. Unverified = "unconfirmed", and verified before any bid effort.
- An opportunity is "open" only if its response deadline is AFTER today. Past-deadline items are recorded as excluded-after-discovery with the date.
- Do not route work to, rely on, or register through any entity the operator has marked EXCLUDED in OR-001 (e.g., sold or divested entities). This program uses only the entities named in OR-001 routes_to.
- Operator approval is required before any bid is actually submitted.

## Tier 2 — SCOPE

- Pursue only opportunities in THIS segment (see PROJECT.md §Segment scope). Cross-segment finds are captured and handed off, not pursued here.
- Capability/geography gaps may be covered by the named subcontracting partner; do not disqualify on capability/location alone.

## Tier 3 — QUALITY

- Every opportunity Finding cites its source (portal/listing URL) by hash or link.
- Prioritize by: eligibility (can we bid now?) > fit > deadline proximity > size/effort.
- Prefer official portals over aggregators for deadline/number verification.

## Tier 4 — STYLE

No operator override beyond schema defaults; citation format per SUBSTRATE.md §Citation Format.

## @@SCAN markers

- @@SCAN-elig: Is SAM.gov active yet? (gates all federal Findings) — answer recorded in OR-001.
- @@SCAN-cadence: What sweep cadence did the operator set? — from OR-001.
