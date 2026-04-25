---
id: T-005
kind: task
schema: client-onboarding
phase: 2
risk_level: standard
required_tools: [file_write]
delivery_mode: constrained
depends_on: [T-004]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-001#<short-hash>]"
acceptance_criteria:
  - "Training agenda matches DEC-001 in-scope features."
  - "Recording (with consent) attached to project artifacts or noted absent."
  - "Q&A captured; surprises proposed as findings or anti-patterns."
---

# Task T-005: Client Training Session
