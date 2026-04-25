---
id: T-000
kind: task
schema: event-planning
phase: 1
risk_level: standard
required_tools: [file_write]
delivery_mode: constrained
depends_on: []
consumes: ["[OR-001#<short-hash>]"]
acceptance_criteria:
  - "Event concept captured as DEC-000 (audience, format, primary outcome)."
  - "Success metrics declared (registrations, attendance, NPS, etc.) with targets."
---

# Task T-000: Concept + Success Metrics

Captures the event's purpose as `DEC-000`. Every downstream task consumes this; changing it forces a council cascade review.
