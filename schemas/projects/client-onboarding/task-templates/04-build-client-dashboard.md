---
id: T-004
kind: task
schema: client-onboarding
phase: 2
risk_level: standard
required_tools: [admin_console, file_write]
delivery_mode: constrained
depends_on: [T-002, T-003]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-001#<short-hash>]"
acceptance_criteria:
  - "Dashboard reflects the in-scope integrations and primary metrics from DEC-001."
  - "Default permissions match least-privilege model."
  - "Client preview link generated and shared with designated contact."
---

# Task T-004: Client-Specific Dashboard
