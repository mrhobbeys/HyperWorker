# PROJECT.md — {{ project_name }}

## Decision statement
{{ decision_statement }}

## Client
{{ client_identity }}
Primary URL(s): {{ client_url }}

## Geography
{{ geography }}  *(do not inherit any prior client's geo)*

## Buyer
{{ buyer }}

## Services
{{ services }}

## Money terms
{{ money_terms }}  *(operator-confirmed in T-000; derived ones flagged for confirmation)*

## Scope mode
{{ scope_mode }}  *(page-rank | vertical-choice | content-gap — gates T-004)*

## Brand / regulatory constraints
{{ brand_constraints }}

## Available data tools
{{ available_tools }}  *(governs realistic MEASURED reach this run)*

## Confidence floor
{{ confidence_floor }}

## Deliverable
{{ deliverable_path }}

## Evidence storage
All discovered artifacts (CMP / FP / GAP / TGT / findings / decisions) append to
`evidence/EVIDENCE-LOG.md`. Multiple agents collaborate through this log; no agent
re-does another's pass.

## Phase shape
- **A — Frame.** Client dossier + OR (T-000).
- **B — Discover.** Competitor discovery (T-001) → footprint (T-002) → gap mining (T-003).
- **C — Evaluate.** Vertical evaluation (T-004, if scope_mode == vertical-choice) + anti-pattern capture (T-005) + target selection (T-006).
- **D — Recommend.** Channel-reality audit (T-007) → recommendation synthesis (T-008) → evidence-integrity audit (T-009).

## Hard scope boundaries
- No recommendation rests on ASSUMED-only inputs; those ship as labeled hypotheses.
- No competitor enters the record without a `found_on` query (no assumed rivals).
- No content target is recommended on a channel-trap-owned SERP.
- No fact, competitor, or target is borrowed from another client's project.
- Brand/regulatory constraints gate every suggested page and headline.

## Completion criteria
- Every recommendation in the deliverable cites MEASURED/OBSERVED by hash (or ESTIMATED on measured inputs).
- ≥1 disconfirming finding present and addressed.
- Channel traps flagged; client scope isolated; brand constraints honored.
- T-009 council converged (or escalated) and operator review complete.
