---
id: T-zz-seo-audit
kind: task
schema: marketing-campaign
phase: end-of-session
risk_level: elevated
required_tools: [file_read, file_write, web_fetch]
optional_tools: [search_console_api]
delivery_mode: constrained
depends_on: []      # operator/planner sets dependencies on the live-edit tasks this audit reviews
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "All eight checks (rank_math metadata, sitemap freshness, robots.txt, redirect coverage, canonical tags, schema markup, internal link graph, Core Web Vitals) executed with PASS/WARN/FAIL recorded."
  - "WARN items are written to deferred-work.md with one-sentence rationale per item."
  - "FAIL items block session.handoff; the report explicitly names which checks blocked."
  - "Output written to outputs/seo-impact-audit-report.md and emitted as a typed artifact."
---

# Task T-zz-seo-impact-audit: SEO Regression Check Before Session Handoff *(elevated risk)*

## Objective

End-of-session audit that verifies the rebrand session did not introduce SEO-negative changes. Runs after all live-edit tasks complete and before `session.handoff`. Surfaces regressions while there is still session context to fix them; defers borderline items; blocks handoff on hard failures.

## When this task runs

This template is conventionally placed at the end of a marketing-campaign session (filename prefix `zz-` sorts after numbered task templates). The planner sets `depends_on:` to include every live-edit task whose output the audit reviews. The audit consumes their completion artifacts plus `OR-001`; it does not need to consume their full pre/post snapshots — it walks the platform itself.

The schema's `default_tasks` includes this task by default. A project may opt out by setting `seo_audit_required: false` in PROJECT.md (e.g., a campaign that doesn't touch SEO surface — a single-channel paid ad that doesn't publish web content).

## Step-by-Step Instructions

### Step 1 — Read the redirect coverage report

Read `projects/<id>/REDIRECT-COVERAGE-REPORT.md` (the v5.1.1 coverage projection from `redirect_implications` aggregation). This is the single source of truth for URL changes the session introduced; subsequent checks cross-reference it.

### Step 2 — Rank Math (or equivalent) metadata audit

For every page in the rollout, compare pre-session and post-session values for:

- `rank_math_title`
- `rank_math_description`
- `rank_math_focus_keyword`

If `rank_math_focus_keyword` shifted in a way that abandons established rankings without a replacement strategy (e.g., a page that ranked #3 for "managed IT services Atlanta" now has focus keyword "cybersecurity compliance" with no successor page targeting the original keyword), record as **FAIL**. If the focus_keyword shifted but the original keyword is still targeted by another in-scope page, record as **PASS**. If the shift is intentional and aligned with the rebrand mission, record as **PASS** with a note.

Title/description changes are normally PASS unless they introduce banned tokens or remove CAN-SPAM-required information from a page that emails reference.

### Step 3 — Sitemap freshness

Fetch `<site>/sitemap.xml` and verify:

- `<lastmod>` dates reflect the rebrand session (within the session window).
- All in-scope URLs are present.
- Trashed/retired URLs are absent.
- New URLs from the rebrand are present.

Missing in-scope URLs = **FAIL**. Stale lastmod dates = **WARN** (cache may not have refreshed yet; flag for follow-up).

### Step 4 — robots.txt

Fetch `<site>/robots.txt`. Verify:

- The file is unchanged from pre-session, OR
- The file changed in a way the rebrand mission explicitly authorized.

An unintended `Disallow: /` or sitewide `noindex` sweep is **FAIL** (catastrophic; immediate rollback discussion).

### Step 5 — Redirect coverage cross-reference

For every row in the redirect coverage report from Step 1:

- `verified` rows: **PASS**.
- `applied` rows without paired `external_state.read_back: divergence_detected: false`: **FAIL** (Patch 2 + Patch 5 should have already caught this; this is the audit's last-line check).
- `planned` rows: **WARN** — operator must decide whether to apply before handoff or defer.
- `deferred` rows: **PASS** with the deferral reason recorded.
- `excluded` rows: **PASS** with the exclusion reason recorded.

Confirm every trashed or renamed URL in the session has a corresponding row. A URL that disappeared from the sitemap but has no row in the coverage report = **FAIL** (a redirect implication was missed).

### Step 6 — Canonical tags

For every rebranded page, fetch and verify the `<link rel="canonical">` tag points to the rebranded URL, not the pre-rebrand URL. Mismatches indicate cache or template propagation issues.

### Step 7 — Schema markup integrity

Fetch any page with structured data (Organization, LocalBusiness, Service). Verify:

- `name`, `legalName`, `address`, `telephone`, `email` are consistent across pages.
- The values match `OR-001.contact_info` (CAN-SPAM physical address + legal name + email).

Inconsistencies = **FAIL** (search engines treat conflicting structured data as untrustworthy).

### Step 8 — Internal link graph spot-check

Pick 3-5 high-value pages (homepage, top-traffic landing pages per pre-session analytics). For each:

- Crawl outbound internal links.
- Verify links point at in-scope rebranded pages, not at trashed or noindex'd content.

Broken or trashed-target internal links = **WARN** (correctable with a single edit; not blocking).

### Step 9 — Core Web Vitals indicator

If a Search Console connector is available (`required_tools: search_console_api`), fetch the latest CWV bucket counts (LCP, INP, CLS). Record the snapshot.

If no connector: this check is **operator-manual** — record as **WARN** with an instruction to run the manual GSC check post-handoff.

## Output: seo_impact_audit_report

Emit `outputs/seo-impact-audit-report.md` as a typed artifact (kind: `seo_impact_audit_report`, schema declares the artifact in v5.1.1+ artifact-extensions if needed). Body:

```markdown
# SEO Impact Audit — <session-id>

| # | Check | Result | Notes |
|---|---|---|---|
| 1 | Redirect coverage report read | PASS \| WARN \| FAIL | <summary> |
| 2 | Rank Math metadata | PASS \| WARN \| FAIL | <summary> |
| 3 | Sitemap freshness | PASS \| WARN \| FAIL | <summary> |
| 4 | robots.txt | PASS \| WARN \| FAIL | <summary> |
| 5 | Redirect coverage cross-reference | PASS \| WARN \| FAIL | <summary> |
| 6 | Canonical tags | PASS \| WARN \| FAIL | <summary> |
| 7 | Schema markup | PASS \| WARN \| FAIL | <summary> |
| 8 | Internal link graph | PASS \| WARN \| FAIL | <summary> |
| 9 | Core Web Vitals | PASS \| WARN \| FAIL | <summary> |

## WARN items (deferred to deferred-work.md)
- ...

## FAIL items (blocking session.handoff)
- ...
```

## Completion Report

- **Acceptance criteria:** <X/Y pass>
- **Citations consumed:** [OR-001#…] + the live-edit tasks whose output was audited
- **Outputs produced:** outputs/seo-impact-audit-report.md
- **WARN items written to deferred-work.md:** <count>
- **FAIL items blocking handoff:** <count>
- **Discoveries:** <items the audit surfaces that don't fit the eight checks but matter>

## Why this exists

Rebrand sessions can introduce SEO regressions silently — a renamed page without a redirect, a focus_keyword shift that abandons a #3 ranking, an unintended `noindex` sweep, structured data that contradicts the new brand. v5.1's empirical run on example-rebrand-rollout surfaced this gap (the rebrand was clean structurally but had no end-of-session SEO check; the operator had to ask for it manually after the fact). v5.1.1 makes this a first-class default task so the regression check happens before handoff, not after.

## Schema integration

This template is included by default in `schemas/projects/marketing-campaign/schema.yaml` `default_tasks.templates`. Projects that don't touch SEO surface opt out by setting `seo_audit_required: false` in PROJECT.md.
