---
id: T-010
kind: task
schema: event-planning
phase: 4
risk_level: critical
required_tools: [file_write]
delivery_mode: constrained
depends_on: [T-008, T-009]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-001#<short-hash>]"
acceptance_criteria:
  - "Run sheet executed; deviations recorded."
  - "Real attendance vs. confirmed counted."
  - "Surprises noted as findings during the day for post-mortem."
---

# Task T-010: Day-Of Execution  *(critical)*

Day-of is critical risk by definition. Council fires 48 hours before via the `pre.event.day` trigger. Mid-day adjustments are recorded in the events log so the post-mortem can reconstruct what actually happened.
