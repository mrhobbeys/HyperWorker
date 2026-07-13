---
id: T-000
kind: task
schema: site-review-repair
phase: 1
risk_level: elevated
task_kind: audit
delivery_mode: constrained
depends_on: []
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "site_domain, platform, access, and definition_of_done confirmed and captured in OR-001."
  - "Bootstrap probe (sitemap+crawl) run; bootstrap.inventory_diff reconciled with operator; scope_locked."
  - "Recovery-program handoff channel recorded (DEC) for any malware items found later."
---

# Task T-000: Scope & Access

Confirm what we are repairing and what access exists. Run the crawl probe and reconcile the page list with the operator before locking scope.
