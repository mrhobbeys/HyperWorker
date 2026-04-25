---
id: T-009
kind: task
schema: event-planning
phase: 3
risk_level: standard
required_tools: [file_write, email_send]
delivery_mode: prescribed
depends_on: [T-007, T-008]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-000#<short-hash>]"
acceptance_criteria:
  - "Confirmation email sent to all registrants 7 days out and 24 hours out."
  - "Email includes logistics: address, parking, start time, dietary accommodation note."
---

# Task T-009: Attendee Confirmations
