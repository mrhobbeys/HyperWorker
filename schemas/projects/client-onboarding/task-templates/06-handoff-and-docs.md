---
id: T-006
kind: task
schema: client-onboarding
phase: 2
risk_level: standard
required_tools: [file_write]
delivery_mode: constrained
depends_on: [T-005]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-001#<short-hash>]"
acceptance_criteria:
  - "Runbook authored covering routine operations + escalation contacts."
  - "Handoff document signed by designated contact (or noted unsigned with reason)."
  - "Cross-project promotion candidates flagged in completion report."
---

# Task T-006: Handoff Package and Runbook

Final task. Produce a runbook for routine operations and an escalation contact list. Flag findings as cross-project promotion candidates so the next onboarding inherits them.
