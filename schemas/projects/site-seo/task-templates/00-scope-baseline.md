---
id: T-000
kind: task
schema: site-seo
phase: 1
risk_level: standard
task_kind: audit
delivery_mode: constrained
depends_on: []
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "GSC property confirmed; indexing/coverage counts, sitemap status, and top queries snapshotted."
  - "Recovery dependency (docroot sitemap/robots fix) status recorded; probe reconciled; scope_locked."
---

# Task T-000: Scope, Access & GSC Baseline

Snapshot the starting line: GSC indexing/coverage, sitemap status, queries/impressions, and whether the Recovery docroot sitemap/robots fix is done or pending.
