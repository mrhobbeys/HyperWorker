# Bootstrap Probe — site-review-repair

> Read by the executor at `hw bootstrap`. Probe = enumerate the site's real pages and compare to declared key pages, so wrong/missing URLs surface at minute one. See `core/SUBSTRATE.md` §Bootstrap Inventory Sweep.

## Probe method
```yaml
probe_method: "sitemap-and-crawl"
steps:
  - fetch: "https://<site_domain>/sitemap.xml (and any sitemap index children)"
  - fallback_fetch: "https://<site_domain>/wp-sitemap.xml or /sitemap_index.xml"
  - crawl: "follow internal links from the homepage one or two levels for pages missing from the sitemap"
produces: "found = list of live URLs with status codes"
```
Emit `bootstrap.inventory_diff` with `declared` = operator-named key pages (from bootstrap answers) and `found` = the crawl result; populate `operator_reconciliation` after the operator confirms; then `bootstrap.scope_locked`.

## Skip path
If the site cannot be crawled at bootstrap (down, or access pending), emit:
```
bootstrap.probe_skipped
  reason: "site not crawlable at bootstrap; operator attested key pages manually"
```
