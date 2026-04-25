---
id: T-007
kind: task
schema: event-planning
phase: 3
risk_level: elevated
required_tools: [file_write, email_send]
delivery_mode: prescribed
depends_on: [T-004, T-005]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-001#<short-hash>]"
acceptance_criteria:
  - "Final headcount confirmed and recorded as DEC-XXX."
  - "Catering vendor notified before their deadline."
  - "Venue notified."
---

# Task T-007: Finalize Headcount
