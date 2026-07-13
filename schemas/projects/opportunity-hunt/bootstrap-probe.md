# Bootstrap Probe — opportunity-hunt

> Read by the executor at `hw bootstrap` time. The probe verifies the declared source/program watch list and eligibility/membership gates against ground truth, so §Scope reflects sources that actually exist and gates that are honestly stated. See `core/SUBSTRATE.md` §Bootstrap Inventory Sweep.

## Default probe — source reachability & eligibility sweep

Opportunity-hunt projects declare eligibility/membership gates (`eligibility_gates`) and, implicitly, a set of sources/programs to monitor. The probe:

1. Collects the sources the operator named at bootstrap (if any) plus the standard set for the declared channel and geographies (cooperative purchasing portals for cooperative-contracts; partner/vendor program portals for channel-partner; grant databases and funder listings for grants-funding; marketplaces, lead platforms, and association boards for commercial-direct).
2. Fetches each source URL (`web_fetch`, falling back to a browser session for JS-gated sources) and records reachability and access level (`open | registration-required | js-gated | login-gated`).
3. Cross-checks the declared `eligibility_gates` object: any gate the operator marked "done" whose program shows no active membership/enrollment path is surfaced for correction; any obviously-required gate the operator did not mention (e.g., vendor award status when a co-op is in scope, partner enrollment when a partner program is in scope) is added to the diff.

The probe records:

- `probe_method: "source-reachability-sweep"`
- `declared`: sources and gates the operator named at bootstrap.
- `found`: sources confirmed reachable, with access level.
- `missing_from_declared`: standard sources for the declared channel/geographies the operator did not name.
- `missing_from_found`: declared sources that were unreachable or ambiguous (wrong URL, renamed, retired program).

## Operator reconciliation

The operator confirms the source watch list per item (monitor / skip with reason) and corrects any dishonestly-optimistic eligibility status. Eligibility/membership gates are recorded as they ARE, not as they are planned to be — the eligibility tier (Tier 1) depends on this being true.

After reconciliation, the agent emits `bootstrap.scope_locked` with the confirmed source list and gate status. PROJECT.md §Scope is written from that event; T-000 (access/eligibility + source inventory) consumes the locked list and registers each confirmed source as a SRC artifact.

## When to skip

If the operator cannot grant network access at bootstrap time, or the source set is operator-curated and already verified (e.g., re-bootstrap of a running channel), the probe emits `bootstrap.probe_skipped` with `reason: "<reason>"`. T-000 assumes responsibility for reachability verification in the skip case.

## Cross-reference to T-000

T-000 (access/eligibility + source inventory) inherits the probe's verified source list rather than building one from scratch. T-000 still registers each source as a SRC artifact with full access metadata and records the eligibility/membership reality in OR-001.
