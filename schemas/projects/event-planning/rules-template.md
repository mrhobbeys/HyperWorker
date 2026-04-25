# 00-REFERENCE-rules.md — <Event Name>

## Precedence Order

When rules conflict, higher tiers override lower tiers. Tier 1 cannot be overridden.

### Tier 1: SAFETY-LEGAL  (absolute — never override)

- Venue fire-code occupancy limits.
- Insurance certificate provided to venue per their lead-time requirement (see AP-* for known venue requirements).
- Alcohol service regulations (jurisdiction-specific).
- Accessibility compliance (ADA or equivalent).
- Vendor contract terms — including deposit-forfeit dates.

@@SCAN_1_1: List SAFETY-LEGAL constraints bearing on this task.
@@SCAN_1_2: Confirm any vendor deposit deadlines this task affects (yes / not-applicable).

### Tier 2: BUDGET  (overrides venue-constraints and experience)

- Total spend ≤ OR-001.budget.amount.
- No new vendor commitment without an existing budget line.
- Non-refundable deposits flagged in DEC-XXX before paying.

@@SCAN_2_1: State the budget line this task draws from and the remaining balance.

### Tier 3: VENUE-CONSTRAINTS  (overrides experience)

- Room capacity ≤ <number>.
- AV capabilities: <list>. Check AP-VENUE-* for venue quirks.
- Load-in/load-out windows: <times>.

@@SCAN_3_1: Name any venue constraint that affects this task's plan.

### Tier 4: EXPERIENCE  (lowest precedence)

- Networking time ≥ presentation time.
- Name badges, not table tents.
- Music during registration window.
