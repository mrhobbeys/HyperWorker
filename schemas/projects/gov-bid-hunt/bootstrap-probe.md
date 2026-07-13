# Bootstrap Probe — gov-bid-hunt

> Read by the executor at `hw bootstrap` time. The probe verifies the declared portal watch list and registration gates against ground truth, so §Scope reflects portals that actually exist and gates that are honestly stated. See `core/SUBSTRATE.md` §Bootstrap Inventory Sweep.

## Default probe — portal reachability sweep

Bid-hunt projects declare registration/eligibility gates (`registration_status`) and, implicitly, a set of portals to monitor. The probe:

1. Collects the portals the operator named at bootstrap (if any) plus the standard set for the declared geographies (SAM.gov for federal; each in-scope state's procurement portal; known aggregators).
2. Fetches each portal URL (`web_fetch`, falling back to a browser session for JS-gated portals) and records reachability and access level (`open | registration-required | js-gated | login-gated`).
3. Cross-checks the declared `registration_status` object: any gate the operator marked "done" whose portal shows no active registration path is surfaced for correction; any obviously-required gate the operator did not mention (e.g., SAM.gov when federal is in scope) is added to the diff.

The probe records:

- `probe_method: "portal-reachability-sweep"`
- `declared`: portals and gates the operator named at bootstrap.
- `found`: portals confirmed reachable, with access level.
- `missing_from_declared`: standard portals for the declared geographies the operator did not name.
- `missing_from_found`: declared portals that were unreachable or ambiguous (wrong URL, renamed, retired).

## Operator reconciliation

The operator confirms the portal watch list per item (monitor / skip with reason) and corrects any dishonestly-optimistic registration status. Registration gates are recorded as they ARE, not as they are planned to be — the eligibility tier (Tier 1) depends on this being true.

After reconciliation, the agent emits `bootstrap.scope_locked` with the confirmed portal list and gate status. PROJECT.md §Scope is written from that event; T-000 (registration + portal inventory) consumes the locked list and registers each confirmed portal as a SRC artifact.

## When to skip

If the operator cannot grant network access at bootstrap time, or the portal set is operator-curated and already verified (e.g., re-bootstrap of a running segment), the probe emits `bootstrap.probe_skipped` with `reason: "<reason>"`. T-000 assumes responsibility for reachability verification in the skip case.

## Cross-reference to T-000

T-000 (registration + portal inventory) inherits the probe's verified portal list rather than building one from scratch. T-000 still registers each portal as a SRC artifact with full access metadata and records the registration/eligibility reality in OR-001.
