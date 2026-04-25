---
id: T-006
kind: task
schema: event-planning
phase: 2
risk_level: standard
required_tools: [file_write, email_send]
delivery_mode: constrained
depends_on: [T-005]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-000#<short-hash>]"
acceptance_criteria:
  - "Promotion plan: channels, send dates, target reach."
  - "Email/social copy drafted; banned-token scan against any general brand-rules file."
  - "Target registrations vs. actual tracked weekly until event."
---

# Task T-006: Promotion Campaign
