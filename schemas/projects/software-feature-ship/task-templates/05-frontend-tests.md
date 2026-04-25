---
id: T-005
kind: task
schema: software-feature-ship
phase: 2
risk_level: standard
required_tools: [file_write, file_read, test_run]
delivery_mode: constrained
depends_on: [T-004]
consumes:
  - "[OR-001#<short-hash>]"
  - "[DEC-000#<short-hash>]"
acceptance_criteria:
  - "Component-level tests for new UI surface."
  - "Test command exits 0."
---

# Task T-005: Frontend Tests

## Steps

1. Recite + SCAN.
2. Author component tests.
3. Run; record exit code.
