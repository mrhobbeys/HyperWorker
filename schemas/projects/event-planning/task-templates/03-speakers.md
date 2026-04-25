---
id: T-003
kind: task
schema: event-planning
phase: 2
risk_level: elevated
required_tools: [file_write, email_send]
delivery_mode: constrained
depends_on: [T-001, T-002]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-000#<short-hash>]"
  - "[DEC-001#<short-hash>]"
acceptance_criteria:
  - "Each speaker confirmed in writing; AV requirements collected."
  - "Speaker fee or honorarium covered by an existing budget line."
  - "Speaker bios and headshots collected for promotion (T-006)."
---

# Task T-003: Speakers
