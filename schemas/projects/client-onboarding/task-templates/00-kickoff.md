---
id: T-000
kind: task
schema: client-onboarding
phase: 1
risk_level: standard
required_tools: [file_write]
delivery_mode: constrained
depends_on: []
consumes:
  - "[OR-001#<short-hash>]"
acceptance_criteria:
  - "Client requirements captured as DEC-001."
  - "Integrations in scope confirmed against OR-001.integrations_in_scope."
  - "Compliance scope acknowledged by client (in writing or recording)."
---

# Task T-000: Kickoff Call

Confirm requirements and scope; capture as `DEC-001`. Open the cross-project anti-pattern review: read subscribed APs and confirm none are surprises to the client.
