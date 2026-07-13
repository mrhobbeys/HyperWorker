# Bootstrap Probe — site-seo

> Probe = read current indexing/ranking state (read-only). See core/SUBSTRATE.md §Bootstrap Inventory Sweep.

```yaml
probe_method: "gsc-indexing-read"
steps:
  - read: "GSC (correct property): Pages/coverage (indexed vs not-indexed + reasons), Sitemaps status, top queries/impressions"
  - fetch: "https://<site_domain>/sitemap_index.xml and /robots.txt (confirm correctness / Recovery-fix status)"
produces: "declared = priority phase order + known counts; found = live GSC/sitemap state"
```
Emit `bootstrap.inventory_diff` (declared vs found) + reconcile, then `bootstrap.scope_locked`. If GSC isn't reachable at bootstrap, emit `bootstrap.probe_skipped` with reason.
