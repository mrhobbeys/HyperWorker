---
id: T-001
kind: task
schema: site-review-repair
phase: 1
risk_level: standard
task_kind: audit
delivery_mode: constrained
depends_on: [T-000]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "Full page inventory captured with HTTP status codes."
  - "Sitemap + redirects recorded as a baseline artifact (Finding or output file)."
---

# Task T-001: Crawl Baseline

Inventory every page: URL, status code, redirects, sitemap coverage. This is the before-state we will repair against.
