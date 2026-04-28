# Bootstrap Probe — marketing-campaign

> Read by the executor at `hw bootstrap` time, after operator answers `bootstrap_questions` and before §Scope locks. The probe surfaces declared-vs-actual mismatches between the operator's declared inventory and ground truth on the live platform. The output drives a `bootstrap.inventory_diff` event; operator reconciliation gates `bootstrap.scope_locked`. See `core/SUBSTRATE.md` §Bootstrap Inventory Sweep.

## Default probe — WordPress

For WordPress-hosted campaigns, the canonical probe is the WP REST pages list:

```
GET /wp-json/wp/v2/pages?status=publish&per_page=100
```

Paginate via `page` parameter until the response is empty or shorter than `per_page`. The probe collects the `slug` field of every published page, normalized to a leading-slash, trailing-slash form (`/about/`, `/managed-it-services/`).

If the campaign also operates on posts (rare; most rebrands target pages), additionally probe `/wp-json/wp/v2/posts` with the same pagination shape.

The probe records:

- `probe_method: "wp-rest-pages-list"`
- `declared`: the slug list the operator provided in `bootstrap_questions` answers (or, for rebrand-rollout missions, the slug list captured under `included_channels` and any explicit page roster).
- `found`: every slug returned by the probe.
- `missing_from_declared`: `found \ declared` — pages on the live site the operator did not list. Prime candidates for in-scope expansion.
- `missing_from_found`: `declared \ found` — pages the operator listed but the live site does not have. Candidates for typo correction or rename detection.

## Operator reconciliation

The agent presents the diff to the operator as three buckets:

1. **Confirm declared.** Items already in `declared` that the probe also found — no action needed. Listed for completeness.
2. **Expand declared.** Items in `missing_from_declared`. For each, operator picks: include in scope, exclude with a reason, or defer.
3. **Correct or remove.** Items in `missing_from_found`. For each, operator picks: provide the correct slug (correction), confirm out-of-scope (the page does not exist and the rebrand does not require creating it), or escalate (the page should exist; investigate before scope locks).

Operator reconciliation is recorded in the `operator_reconciliation` field of `bootstrap.inventory_diff`. After reconciliation, the agent emits `bootstrap.scope_locked` with the reconciled `scope_items` list and PROJECT.md §Scope is written from that event.

## Non-WordPress hosts

For non-WordPress campaigns, the probe method is platform-specific. Document the probe and reconciliation flow before bootstrap. Common platforms:

- **Webflow.** `GET /v2/sites/{site_id}/pages` (auth required). Same diff shape; `probe_method: "webflow-pages-list"`.
- **Ghost.** `GET /admin/api/v5/pages/?limit=all` (auth required). `probe_method: "ghost-pages-list"`.
- **Shopify (custom pages).** `GET /admin/api/2024-01/pages.json` (auth required). `probe_method: "shopify-pages-list"`.

Stub the platform integration if the campaign's host is not yet covered. The agent records `probe_method: "schema-declared-stub-pending-platform"` and emits `bootstrap.probe_skipped` with `reason: "<platform> probe not implemented; operator manually attested inventory"`.

## Static-site hosts (no API)

For Jekyll / Hugo / Eleventy / hand-rolled static-site builds, the probe is filesystem-based: walk the source-content directory, read frontmatter for any page-like content type, and emit slugs. `probe_method: "filesystem-static-site"`. Document the source-content directory in the project's bootstrap answers so the probe knows where to walk.

## When to skip the probe

If none of the above apply (operator runs the campaign on a closed platform with no introspection surface, or a brand-new site with no published pages yet), the agent emits `bootstrap.probe_skipped` with a reason that documents what would have been probed and why no probe was practical. The skip is a structural fact in the chain; downstream verification distinguishes "skipped with reason" from "probe was forgotten."
