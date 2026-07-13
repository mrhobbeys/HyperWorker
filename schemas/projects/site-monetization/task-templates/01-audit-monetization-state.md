---
id: T-001
kind: task
schema: site-monetization
phase: 1
risk_level: standard
task_kind: audit
delivery_mode: constrained
depends_on: [T-000]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "AdSense onboarding/connection state recorded; Ezoic integration + MEDIATION link status recorded."
  - "Identity coverage, ad placements/density, ads.txt, and video-program status recorded."
---

# Task T-001: Audit Monetization State

Read current state: AdSense onboarding/connection; Ezoic integration and whether AdSense is linked in Mediation; identity coverage; placements; ads.txt; video program. Read-only.
