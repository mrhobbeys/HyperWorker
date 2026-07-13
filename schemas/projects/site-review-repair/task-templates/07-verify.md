---
id: T-007
kind: task
schema: site-review-repair
phase: 3
risk_level: elevated
task_kind: verify
delivery_mode: constrained
depends_on: [T-006]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "Each fix re-fetched on production and confirmed resolved (record the URL + result)."
  - "Regression check: spot-check other pages/templates not broken."
---

# Task T-007: Verify on Production

Re-fetch production and prove each fix landed. Spot-check for regressions. A fix is not done until verified.
