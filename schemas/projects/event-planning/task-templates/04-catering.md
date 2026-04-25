---
id: T-004
kind: task
schema: event-planning
phase: 2
risk_level: elevated
required_tools: [file_write, email_send]
delivery_mode: constrained
depends_on: [T-001, T-002]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-001#<short-hash>]"
acceptance_criteria:
  - "Catering vendor selected; menu confirmed against OR-001.format and dietary requirements."
  - "Minimum-headcount guarantee documented in DEC-XXX (cross-project AP: minimum often calculated against capacity, not RSVPs)."
  - "Cancellation deadline added to calendar."
---

# Task T-004: Catering
