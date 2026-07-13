# Bootstrap Probe — brand-ecosystem-audit

> Inventories the brand's actual surfaces before §Scope locks, so the property list is ground
truth, not recollection.

## Default probe — surface sweep
From OR.surfaces (and the owned hub's own links/footer/social icons), confirm each surface:
```
for each declared surface: resolve url/handle in a browser
  record: platform, url_or_handle, role (owned-hub/owned-secondary/social/marketplace/review),
          status (live | dead(NXDOMAIN/broken) | wrong-handle | duplicate | missing)
also scan the owned hub for OUTBOUND brand links -> catches typo domains, dead links, wrong handles
```
Record `declared` (operator's list), `found` (resolved surfaces), `missing_from_declared`
(surfaces discovered on the hub the operator didn't name — e.g. a second IG handle), and
`dead_or_wrong` (NXDOMAIN typos, wrong-handle links). The operator reconciles in one pass.

After reconciliation emit `bootstrap.scope_locked` with the property list. T-000 consumes it.

## Dispatch-mode note
If any social/login surface is present, default `dispatch_mode: separate-chats` (each needs an
agent-driven browser with human login assist; subagents can't hold the session). <=4 low-risk
surfaces may run single-agent. The operator confirms.

## When to skip
If the owned hub is unreachable or pre-launch, emit `bootstrap.probe_skipped` with the reason;
T-000 inventories from operator-supplied handles and marks unresolved surfaces as open items.
