---
id: T-006
kind: task
schema: site-monetization
phase: 3
risk_level: elevated
task_kind: verify
delivery_mode: constrained
depends_on: [T-005]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "After operator executes, re-check: primary network connected, mediation linked (if a mediation platform is in scope), ads.txt correct."
  - "Note low-traffic caveat where impressions are too sparse to confirm serving."
---

# Task T-006: Verify

Re-check that the executed steps landed (primary network connected, e.g., AdSense; mediation linked if applicable, e.g., Ezoic; ads.txt correct). Note traffic caveats.
