---
id: T-011
kind: task
schema: event-planning
phase: 4
risk_level: standard
required_tools: [file_write, email_send]
delivery_mode: constrained
depends_on: [T-010]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-000#<short-hash>]"
acceptance_criteria:
  - "Follow-up email sent within 48 hours of event."
  - "Feedback survey distributed; responses captured as findings."
  - "Venue-specific anti-patterns captured if any new ones surfaced."
  - "Post-mortem narrative authored in done/T-011/post-mortem.md (file-canonical)."
---

# Task T-011: Follow-up + Post-mortem

Final task. Captures findings (audience preferences, vendor performance) and venue-specific anti-patterns so the next event at the same venue inherits them. Post-mortem is narrative prose in the Mutable Surface, not event-sourced.
