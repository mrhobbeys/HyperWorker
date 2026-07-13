# Bootstrap Probe — site-monetization

> Probe = read the site's current monetization signals (read-only). See core/SUBSTRATE.md §Bootstrap Inventory Sweep.

```yaml
probe_method: "monetization-state-read"
steps:
  - fetch: "https://<site_domain>/ads.txt  (check for the AdSense pub id + Ezoic lines)"
  - read: "AdSense dashboard onboarding/site-connection state (operator-assisted if login needed)"
  - read: "Ezoic dashboard: integration, mediation (AdSense linked?), identity coverage, ad placements, video program"
produces: "declared = operator-stated goals; found = current live monetization state"
```
Emit `bootstrap.inventory_diff` (declared vs found) + reconcile, then `bootstrap.scope_locked`. If dashboards need operator login not yet available, emit `bootstrap.probe_skipped` with reason.
