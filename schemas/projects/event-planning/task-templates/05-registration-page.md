---
id: T-005
kind: task
schema: event-planning
phase: 2
risk_level: elevated
required_tools: [file_write, web_browse, web_fetch]
delivery_mode: constrained
depends_on: [T-000, T-001]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-000#<short-hash>]"
  - "[DEC-001#<short-hash>]"
acceptance_criteria:
  - "Registration page live with form fields scoped (name, email, dietary restrictions, accessibility needs)."
  - "Capacity cap matches venue capacity minus speaker/staff allocation."
  - "Confirmation email triggers on submit; tested with the operator's email."
---

# Task T-005: Registration Page
