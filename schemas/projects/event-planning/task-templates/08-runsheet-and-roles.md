---
id: T-008
kind: task
schema: event-planning
phase: 3
risk_level: elevated
required_tools: [file_write]
delivery_mode: constrained
depends_on: [T-003, T-007]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-000#<short-hash>]"
  - "[DEC-001#<short-hash>]"
acceptance_criteria:
  - "Run sheet covers every 15-minute block from doors-open to load-out."
  - "Every block has a named owner."
  - "Speaker AV requirements addressed in their corresponding blocks."
---

# Task T-008: Run Sheet + Role Assignments
