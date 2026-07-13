---
id: T-000
kind: task
schema: site-monetization
phase: 1
risk_level: standard
task_kind: audit
delivery_mode: constrained
depends_on: []
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "site_domain, adsense_pubid, ezoic_id, access, and monetization_goal captured in OR-001."
  - "Probe run (ads.txt + dashboards); inventory_diff reconciled; scope_locked (or probe_skipped w/ reason)."
---

# Task T-000: Scope & Access

Confirm the monetization targets and what access exists. Probe ads.txt and the AdSense/Ezoic dashboards (operator-assisted for logins).
