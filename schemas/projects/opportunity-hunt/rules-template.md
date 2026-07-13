# 00-REFERENCE-rules — {{ project_name }} (opportunity-hunt)

Precedence tiers resolve rule conflicts (see precedence-tiers.yaml). Highest tier wins.

## Tier 1 — ABSOLUTE
- Never push a pursuit the business can't currently execute; flag the eligibility/membership gate instead of dropping it.
- Never fabricate a contact, price, deadline, or program rule. Unverified = "unconfirmed", verified before pursuit.
- Operator approval is required before any outreach, proposal, application, or submission is sent. Draft only; the operator sends.
- Honor OR-001 company facts: delivery model and subcontracting coverage come from OR-001 (capability/geography gaps go to the OR-001 subcontracting partner, if one is named); route out-of-channel finds to the right project.

## Tier 2 — SCOPE
- Pursue only this channel's scope (see PROJECT.md). Cross-channel finds are captured and handed off.

## Tier 3 — QUALITY
- Every opportunity Finding cites its source by hash/link.
- Prioritize: eligibility (can we act now?) > fit > value > effort > deadline proximity.
- Prefer official/primary sources for figures and deadlines.

## Tier 4 — STYLE
No operator override beyond schema defaults; citation format per SUBSTRATE.md.

## @@SCAN markers
- @@SCAN-elig: what membership/eligibility gates this channel? (from OR-001)
- @@SCAN-cadence: sweep cadence? (from OR-001)
