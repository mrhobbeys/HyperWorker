---
id: T-003
kind: task
schema: client-onboarding
phase: 1
risk_level: standard
required_tools: [admin_console, file_write]
delivery_mode: prescribed
depends_on: [T-001]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-001#<short-hash>]"
acceptance_criteria:
  - "Each integration in OR-001.integrations_in_scope configured."
  - "Each integration's connection tested and recorded."
  - "Configuration decisions captured as DEC-XXX (one per integration)."
---

# Task T-003: Configure Integrations

For each in-scope integration, configure and test. Capture configuration decisions as artifacts so the next client onboarding can read them via cross-project subscription if applicable.
