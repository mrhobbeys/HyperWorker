# Bootstrap Probe — site-monetization

> Probe = read the site's current monetization signals (read-only). See core/SUBSTRATE.md §Bootstrap Inventory Sweep.

```yaml
probe_method: "monetization-state-read"
steps:
  - fetch: "https://<site_domain>/ads.txt  (check for the primary-network publisher line + mediation-platform lines, e.g., AdSense pub id + Ezoic)"
  - read: "Primary ad network dashboard onboarding/site-connection state (e.g., AdSense; operator-assisted if login needed)"
  - read: "Mediation/optimization platform dashboard, if one is in scope (e.g., Ezoic): integration, mediation (is the primary network linked?), identity coverage, ad placements, video program"
produces: "declared = operator-stated goals; found = current live monetization state"
```
Emit `bootstrap.inventory_diff` (declared vs found) + reconcile, then `bootstrap.scope_locked`. If dashboards need operator login not yet available, emit `bootstrap.probe_skipped` with reason.
