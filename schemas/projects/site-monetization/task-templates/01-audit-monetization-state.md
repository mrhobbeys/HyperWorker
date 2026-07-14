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
  - "Primary-network onboarding/connection state recorded; mediation-platform integration + link status recorded (if a mediation platform is in scope)."
  - "Identity coverage, ad placements/density, ads.txt, and video-program status recorded."
---

# Task T-001: Audit Monetization State

Read current state: primary ad network onboarding/connection (e.g., AdSense); mediation-platform integration and whether the primary network is linked in mediation (e.g., Ezoic); identity coverage; placements; ads.txt; video program. Read-only.
