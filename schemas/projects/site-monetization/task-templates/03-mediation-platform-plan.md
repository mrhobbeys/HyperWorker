---
id: T-003
kind: task
schema: site-monetization
phase: 2
risk_level: elevated
task_kind: plan
delivery_mode: constrained
depends_on: [T-001]
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "Prioritized mediation-platform optimization plan: identity coverage, rewarded ads, placements, ads.txt. Skip this task (mark not-applicable) if no mediation platform is in scope."
  - "Respects the operator ad-density goal."
---

# Task T-003: Mediation Platform Plan

Draft prioritized improvements on the mediation/optimization platform (e.g., Ezoic): identity coverage, rewarded ads, placements, ads.txt. Honor the ad-density goal. If no mediation platform is in use (primary network only), mark this task not-applicable and record why.
